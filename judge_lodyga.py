#!/usr/bin/env python3
"""Judge Łodyga answers through an OpenAI-compatible chat-completions API.

Implements the Łodyga 0.1 protocol from custom_scoring.md: four-dimension 0-10
rubric, per-turn references, single-user-message prompts, strict JSON validation
without retries (invalid judge output is recorded as unscored), and raw
request/response archiving. Each run judges the whole answer file and rewrites
its outputs, so a judgment file always describes exactly one run.
"""

import argparse
import json
import os
import sys
import threading
import time
import tomllib
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import runs

PROTOCOL = "Łodyga 0.1"

# Rubric block shared by both turn templates, verbatim from custom_scoring.md.
RUBRIC = """\
Jesteś bezstronnym, wymagającym recenzentem odpowiedzi asystentów AI w języku polskim.
Oceń odpowiedź użytkową, a nie długość rozumowania. Długie rozumowanie jest w porządku,
jeśli prowadzi do poprawnej i użytecznej odpowiedzi; odejmuj punkty tylko wtedy, gdy
powtarza się, zawiera błędy, odchodzi od zadania albo utrudnia znalezienie odpowiedzi.

Przyznaj punkty w czterech wymiarach:
- correctness: 0–4, poprawność i faktyczność;
- task_completion: 0–3, wykonanie polecenia i ograniczeń;
- usefulness: 0–2, kompletność i przydatność;
- polish: 0–1, naturalność polszczyzny i czytelność.

Suma musi być liczbą całkowitą od 0 do 10. Zwróć wyłącznie JSON:
{"correctness": 0, "task_completion": 0, "usefulness": 0, "polish": 0,
 "total": 0, "explanation": "krótkie uzasadnienie po polsku"}"""

TURN2_INSTRUCTION = """\
Oceń przede wszystkim odpowiedź na DRUGIE pytanie, uwzględniając pierwsze pytanie
oraz pierwszą odpowiedź jako kontekst. Sprawdź, czy asystent rzeczywiście wykonał
zmianę, korektę lub dodatkowe zadanie z drugiego pytania. Zastosuj dokładnie te same
cztery wymiary i zwróć wyłącznie ten sam format JSON."""

# Dimension name -> maximum points.
DIMENSIONS = {"correctness": 4, "task_completion": 3, "usefulness": 2, "polish": 1}


def reference_text(value, turn):
    """Return the reference text for a turn, or None when absent/empty."""
    if value is None:
        return None
    if isinstance(value, list):
        if turn >= len(value):
            return None
        value = value[turn]
    if not isinstance(value, str):
        value = str(value)
    return value.strip() or None


def prompt_turn1(question, reference, answer):
    parts = [RUBRIC, "PYTANIE:\n" + question]
    if reference:
        parts.append(
            "REFERENCJA (opcjonalna; traktuj ją jako wskazówkę, nie jako tekst do kopiowania):\n"
            + reference
        )
    parts.append("ODPOWIEDŹ ASYSTENTA:\n" + answer)
    return "\n\n".join(parts)


def prompt_turn2(question_1, answer_1, reference_1, question_2, reference_2, answer_2):
    parts = [
        RUBRIC,
        TURN2_INSTRUCTION,
        "PIERWSZE PYTANIE:\n" + question_1,
        "PIERWSZA ODPOWIEDŹ:\n" + answer_1,
    ]
    if reference_1:
        parts.append("REFERENCJA DO PIERWSZEGO PYTANIA (opcjonalna):\n" + reference_1)
    parts.append("DRUGIE PYTANIE:\n" + question_2)
    if reference_2:
        parts.append("REFERENCJA (opcjonalna):\n" + reference_2)
    parts.append("DRUGA ODPOWIEDŹ — OCENIANA:\n" + answer_2)
    return "\n\n".join(parts)


def extract_json(text):
    """Strip whitespace and one optional markdown code fence."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
        text = text.strip()
    return text


def as_integer(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value != int(value):
        return None
    return int(value)


def validate(content):
    """Parse and validate one judge response.

    Returns (judgment, None) on success, or (None, reason). No retries and no
    imputation: anything unexpected is recorded as unscored.
    """
    try:
        data = json.loads(extract_json(content))
    except ValueError:
        return None, "invalid_json"
    if not isinstance(data, dict):
        return None, "invalid_json"
    scores = {}
    for name, maximum in DIMENSIONS.items():
        if name not in data:
            return None, "missing_field"
        value = as_integer(data[name])
        if value is None or not 0 <= value <= maximum:
            return None, "invalid_score"
        scores[name] = value
    if "total" not in data:
        return None, "missing_field"
    total = as_integer(data["total"])
    if total is None:
        return None, "invalid_score"
    if total != sum(scores.values()):
        return None, "total_mismatch"
    explanation = data.get("explanation")
    if not isinstance(explanation, str):
        return None, "invalid_explanation"
    judgment = {**scores, "total": total, "explanation": explanation}
    return judgment, None


def load_dotenv(path=None):
    """Minimal .env loader; real environment variables take precedence.

    Resolved next to this file rather than in the working directory, so the
    runner finds the key no matter where it is invoked from.
    """
    path = Path(path) if path else runs.PROJECT_DIR / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def chat(cfg, prompt):
    """POST one chat completion; returns (response, payload).

    Retries only transient transport errors. Judge-output validation failures are
    handled by the caller and are never retried, per custom_scoring.md.
    """
    api = cfg["api"]
    payload = {"model": api["model"], "messages": [{"role": "user", "content": prompt}]}
    payload.update(cfg.get("generation", {}))
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    key_name = api.get("api_key_env", "OPENROUTER_API_KEY")
    key = os.environ.get(key_name)
    if key:
        headers["Authorization"] = f"Bearer {key}"
    url = api["base_url"].rstrip("/") + "/chat/completions"
    retries = int(api.get("max_retries", 5))
    for attempt in range(retries + 1):
        if attempt:
            time.sleep(2 ** (attempt - 1))
        request = urllib.request.Request(url, body, headers)
        try:
            with urllib.request.urlopen(request, timeout=api.get("timeout", 600)) as response:
                return json.load(response), payload
        except urllib.error.HTTPError as error:
            transient = error.code in (408, 429, 500, 502, 503, 504)
            detail = f"HTTP {error.code} {error.read().decode(errors='replace')[:200]}"
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            transient = True
            detail = getattr(error, "reason", error)
        if not transient or attempt >= retries:
            raise RuntimeError(
                f"judge request failed after {attempt + 1} attempt(s): {detail}"
            )


def load_answers(path):
    answers = {}
    model_id = None
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if model_id is None and row.get("model_id"):
            model_id = row["model_id"]
        turns = row.get("choices", [{}])[0].get("turns", [])
        if len(turns) == 2:
            answers[row["question_id"]] = turns
    return answers, model_id


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="judge config TOML")
    parser.add_argument(
        "--run-dir",
        help="run directory to judge, or 'latest'; answers and outputs live there",
    )
    parser.add_argument(
        "--answers",
        type=Path,
        help="answers JSONL to judge instead of a run directory's answers.jsonl",
    )
    parser.add_argument(
        "--questions",
        type=Path,
        default=runs.QUESTIONS,
        help="Łodyga question file",
    )
    parser.add_argument("--output", type=Path, help="judgments JSONL output path")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=80,
        help="turns judged at once; overridden by api.concurrency in the judge config",
    )
    args = parser.parse_args(argv)
    if not args.answers and not args.run_dir:
        parser.error("one of --run-dir or --answers is required")

    cfg_text = args.config.read_text()
    cfg = tomllib.loads(cfg_text)
    run_dir = None
    if args.answers and not args.run_dir:
        answers_file = args.answers
        output = args.output or answers_file.with_name(answers_file.stem + "__judgments.jsonl")
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = runs.resolve_run_dir(args.run_dir)
        answers_file = args.answers or runs.answers_path(run_dir)
        if not answers_file.exists():
            sys.exit(f"error: no answers in {run_dir}; run generation first")
        output = args.output or runs.judgments_path(run_dir)
        runs.archive_config(run_dir, "judge", args.config)
        runs.update_stage(run_dir, "judge", "running")
        print(f"run directory: {run_dir}", flush=True)
    raw_path = output.with_name(output.stem + "__raw.jsonl")
    meta_path = output.with_name(output.stem + "__meta.json")

    load_dotenv()
    key_name = cfg["api"].get("api_key_env", "OPENROUTER_API_KEY")
    if not os.environ.get(key_name):
        sys.exit(f"error: {key_name} is not set; add it to .env or export it")

    lines = [line for line in args.questions.read_text().splitlines() if line.strip()]
    questions = [json.loads(line) for line in lines]
    answers, model_id = load_answers(answers_file)
    model_id = model_id or answers_file.stem

    start = time.time()
    summary = {"scored": 0, "unscored": {}}

    # Unlike generation, both turns are judged from the finished answer file, so
    # every (question, turn) is independent and the whole set can run at once.
    units = []
    for q in questions:
        qid = q["question_id"]
        turns = answers.get(qid)
        if turns is None:
            print(f"{model_id}: question {qid} skipped (no answer row)")
            continue
        units.append(
            (qid, 1, prompt_turn1(q["turns"][0], reference_text(q.get("reference"), 0), turns[0]))
        )
        units.append(
            (
                qid,
                2,
                prompt_turn2(
                    q["turns"][0],
                    turns[0],
                    reference_text(q.get("reference"), 0),
                    q["turns"][1],
                    reference_text(q.get("reference"), 1),
                    turns[1],
                ),
            )
        )

    workers = max(1, int(cfg["api"].get("concurrency", args.concurrency)))
    lock = threading.Lock()

    def judge_unit(unit):
        qid, turn, prompt = unit
        response, payload = chat(cfg, prompt)
        content = response.get("choices", [{}])[0].get("message", {}).get("content")
        raw = {
            "question_id": qid,
            "turn": turn,
            "request": payload,
            "response": response,
            "tstamp": time.time(),
        }
        if content is None:
            judgment, reason = None, "empty_response"
        else:
            judgment, reason = validate(content)
        row = {
            "question_id": qid,
            "model_id": model_id,
            "judge_model": cfg["api"]["model"],
            "turn": turn,
            "tstamp": time.time(),
        }
        with lock:
            if judgment is None:
                row["status"] = "unscored"
                row["reason"] = reason
                summary["unscored"][reason] = summary["unscored"].get(reason, 0) + 1
                print(f"{model_id}: question {qid} turn {turn} unscored ({reason})", flush=True)
            else:
                row["status"] = "scored"
                row["judgment"] = judgment
                summary["scored"] += 1
                print(
                    f"{model_id}: question {qid} turn {turn} total {judgment['total']}", flush=True
                )
        return row, raw

    print(f"{model_id}: judging {len(units)} turns with {workers} workers", flush=True)
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(judge_unit, units))
    except Exception as error:
        if run_dir is not None:
            runs.update_stage(run_dir, "judge", "failed", error=repr(error))
        raise
    # Written in (question, turn) order regardless of completion order, so the
    # outputs are comparable across runs. Every run rewrites them in full.
    with output.open("w") as fout, raw_path.open("w") as fraw:
        for row, raw in results:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
            fraw.write(json.dumps(raw, ensure_ascii=False) + "\n")

    meta = {
        "protocol": PROTOCOL,
        "judge_model": cfg["api"]["model"],
        "answers_file": str(answers_file),
        "questions_file": str(args.questions),
        "judge_config_file": str(args.config),
        "judge_config": cfg,
        "sampling": dict(cfg.get("generation", {})),
        "started": start,
        "finished": time.time(),
        "summary": summary,
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    if run_dir is not None:
        runs.update_stage(
            run_dir,
            "judge",
            "complete",
            judge_model=cfg["api"]["model"],
            sampling=dict(cfg.get("generation", {})),
            scored=summary["scored"],
            unscored=summary["unscored"],
        )
    print(
        f"{model_id}: {summary['scored']} scored, "
        f"{sum(summary['unscored'].values())} unscored -> {output}"
    )
    return run_dir


if __name__ == "__main__":
    main()