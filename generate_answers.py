#!/usr/bin/env python3
"""Generate Łodyga answers through an OpenAI-compatible /completions API."""

import argparse
import json
import threading
import time
import tomllib
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import runs

PROTOCOL = "Łodyga 0.1"


def load_tokenizer(cfg):
    from transformers import AutoTokenizer

    path = cfg["model"]["tokenizer"]
    subfolder = cfg["model"].get("tokenizer_subfolder")
    if subfolder:
        from huggingface_hub import snapshot_download

        path = Path(snapshot_download(path, allow_patterns=[f"{subfolder}/*"])) / subfolder
    tokenizer = AutoTokenizer.from_pretrained(
        str(path), trust_remote_code=cfg["model"].get("trust_remote_code", False)
    )
    # Część modeli instruct nie ma `chat_template` w tokenizer_config.json, choć
    # karta modelu podaje format promptu. Wtedy szablon wpisuje się wprost do
    # configu, w `chat_template.template`, i to on jest źródłem prawdy.
    template = cfg.get("chat_template", {}).get("template")
    if template:
        tokenizer.chat_template = template
    return tokenizer


def hosted_model_id(cfg):
    """Served model name from the config; the /models endpoint is a fallback.

    Resolved once per run so generation does not re-query the server.
    """
    api = cfg["api"]
    if api.get("model"):
        return api["model"]
    req = urllib.request.Request(api["base_url"].rstrip("/") + "/models")
    with urllib.request.urlopen(req, timeout=api.get("timeout", 600)) as response:
        served = json.load(response)["data"][0]["id"]
    print(f"api.model is empty; using served model {served!r} from /models")
    return served


def complete(cfg, model, prompt_ids):
    api = cfg["api"]
    generation = dict(cfg.get("generation", {}))
    payload = {"model": model, "prompt": prompt_ids, **generation}
    payload.pop("base_url", None)
    payload.pop("api_key_env", None)
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    key_name = api.get("api_key_env")
    if key_name:
        import os

        key = os.environ.get(key_name)
        if key:
            headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(api["base_url"].rstrip("/") + "/completions", body, headers)
    with urllib.request.urlopen(req, timeout=api.get("timeout", 600)) as response:
        result = json.load(response)
    return result["choices"][0]["text"]


def chat_complete(cfg, model, messages, enable_thinking):
    """One /v1/chat/completions call; returns (reasoning, answer).

    Here the server renders its own chat template, so no tokenizer is needed.
    `enable_thinking` is forwarded as `chat_template_kwargs`, which SGLang and
    vLLM pass through to the template.

    Servers started with a reasoning parser split the trace into
    `reasoning_content` and leave `content` clean; without one the trace arrives
    inline in `content` and is separated by the caller.
    """
    api = cfg["api"]
    payload = {"model": model, "messages": messages, **dict(cfg.get("generation", {}))}
    if enable_thinking is not None:
        payload["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
    body = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    key_name = api.get("api_key_env")
    if key_name:
        import os

        key = os.environ.get(key_name)
        if key:
            headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        api["base_url"].rstrip("/") + "/chat/completions", body, headers
    )
    with urllib.request.urlopen(req, timeout=api.get("timeout", 600)) as response:
        result = json.load(response)
    message = result["choices"][0]["message"]
    return message.get("reasoning_content") or "", message.get("content") or ""


def render(tokenizer, messages, enable_thinking=None, prefill=""):
    """Wyrenderuj prompt lokalnie, opcjonalnie doklejając prefill odpowiedzi.

    `prefill` to tekst dopisany po `<|im_start|>assistant`, zanim model zacznie
    generować. Służy do wymuszenia zachowania, którego szablon nie potrafi sam:
    `"<think>\\n</think>\\n"` zamyka blok rozumowania z góry, więc model nie ma
    czego kontynuować i odpowiada od razu. Tak da się wyłączyć myślenie w
    modelach, których szablon nie zna `enable_thinking`.
    """
    kwargs = {"tokenize": False, "add_generation_prompt": True}
    if enable_thinking is not None:
        kwargs["enable_thinking"] = enable_thinking
    prompt = tokenizer.apply_chat_template(messages, **kwargs) + prefill
    # Match the tested SGLang path: send exact token IDs and prevent the server
    # from adding a BOS token or rendering a second chat template.
    return tokenizer.encode(prompt, add_special_tokens=False)


def clean_answer(text):
    """Keep server-returned text out of the next chat-template turn."""
    # /completions returns only the completion, but some servers include the
    # generated end-of-turn token when no stop sequence was configured.
    for marker in ("<|im_end|>", "<|eot_id|>", "<|end_of_turn|>"):
        if marker in text:
            text = text.split(marker, 1)[0]
    for marker in ("<|im_start|>assistant", "<|im_start|> assistant"):
        if text.lstrip().startswith(marker):
            text = text.lstrip()[len(marker):]
    return text.strip()


def split_reasoning(text, prefilled):
    """Separate one completion into (reasoning, answer).

    With `enable_thinking = true` the chat template ends the prompt with an open
    `<think>` tag, so the completion starts inside the reasoning block and the
    model closes it with `</think>` before answering. `prefilled` says whether
    the template opened that block for us; a model that emits its own `<think>`
    is handled too.

    Only the answer is ever judged — the reasoning trace is archived, never
    scored (see custom_scoring.md).
    """
    opened = prefilled
    if text.startswith("<think>"):
        text = text[len("<think>"):]
        opened = True
    reasoning, closed, answer = text.partition("</think>")
    if closed:
        return reasoning.strip(), answer.strip()
    if opened:
        # The block never closed: the model spent its whole budget reasoning
        # and delivered no answer. Record that instead of promoting the trace
        # to an answer, which would put the trace in front of the judge.
        return text.strip(), ""
    return "", text.strip()


def answer_turn(cfg, model, tokenizer, messages, think, prefilled, mode, prefill=""):
    """Generate one turn; returns (reasoning, answer).

    Both endpoints end up in the same place: the trace separated from the
    answer, so only the answer is ever judged.
    """
    if mode == "chat":
        reasoning, content = chat_complete(cfg, model, messages, think)
        if reasoning.strip():
            # The server already split the trace out for us.
            return reasoning.strip(), clean_answer(content)
        # No reasoning parser on the server: the trace is inline, exactly as on
        # the /completions path.
        return split_reasoning(clean_answer(content), prefilled)
    prompt_ids = render(tokenizer, messages, think, prefill)
    return split_reasoning(clean_answer(complete(cfg, model, prompt_ids)), prefilled)


def assistant_message(answer):
    """Turn-1 message for the turn-2 prompt: the answer only.

    The turn-1 reasoning trace is deliberately dropped from turn-2 context. This
    template would otherwise preserve it (it renders `reasoning_content` back
    into a `<think>` block), but the follow-up is supposed to be answered from
    the visible conversation, exactly as a user would see it. Keeping the trace
    would also spend the 8192-token window twice over on long reasoning.

    The trace is still archived in the answer file; it is simply not context.
    """
    return {"role": "assistant", "content": answer}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--questions", type=Path, default=runs.QUESTIONS)
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="write into this existing run directory instead of creating a new one",
    )
    parser.add_argument("--output", type=Path, help="write answers here instead of a run directory")
    parser.add_argument(
        "--concurrency",
        type=int,
        default=80,
        help="questions in flight at once; overridden by api.concurrency in the config",
    )
    args = parser.parse_args(argv)
    cfg = tomllib.loads(args.config.read_text())
    model_id = cfg["model"]["id"]
    # A new timestamped run directory per invocation; nothing is ever
    # overwritten. --output remains for one-off files (tests, spot checks).
    run_dir = None
    if args.output:
        output = args.output
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = args.run_dir or runs.new_run_dir(model_id)
        output = runs.answers_path(run_dir)
        runs.archive_config(run_dir, "model", args.config)
        meta = runs.read_meta(run_dir)
        meta.update(
            {
                "protocol": PROTOCOL,
                "model_id": model_id,
                "questions_file": str(args.questions),
                "model_config": cfg,
            }
        )
        runs.write_meta(run_dir, meta)
        runs.update_stage(run_dir, "generate", "running")
        print(f"run directory: {run_dir}", flush=True)
    # Domyślnie "completions": szablon czatu renderujemy lokalnie i wysyłamy
    # gotowe ID tokenów, bo tylko tak mamy pewną kontrolę nad blokiem <think>.
    # Przez chat API sterowanie reasoningiem bywa zawodne - serwer może zignorować
    # chat_template_kwargs albo model i tak wstawi własny <think>. Tryb "chat"
    # jest dla modeli, które to obsługują poprawnie; nie potrzebuje tokenizera.
    mode = cfg["api"].get("mode", "completions")
    if mode not in ("completions", "chat"):
        raise SystemExit(f"error: api.mode musi być 'completions' albo 'chat', nie {mode!r}")
    tokenizer = load_tokenizer(cfg) if mode == "completions" else None
    model = hosted_model_id(cfg)
    questions = [json.loads(line) for line in args.questions.read_text().splitlines() if line]
    think = cfg.get("chat_template", {}).get("enable_thinking")
    # Prefill odpowiedzi asystenta, doklejany po prompcie generacji. Działa tylko
    # przy mode = "completions", bo tylko tam budujemy prompt sami.
    prefill = cfg.get("chat_template", {}).get("prefill", "")
    if prefill and mode != "completions":
        raise SystemExit("error: chat_template.prefill wymaga api.mode = 'completions'")
    # `enable_thinking = false` makes the template close the block immediately,
    # so only an explicit true leaves an open <think> for the model to finish.
    # Prefill decyduje o tym samym, jeśli jest ustawiony: liczy się to, czy
    # prompt kończy się otwartym blokiem rozumowania.
    prefilled = prefill.rstrip().endswith("<think>") if prefill else think is True
    # Questions are independent, so they run concurrently; the two turns of one
    # question stay sequential because turn 2 needs turn 1 in its prompt.
    workers = max(1, int(cfg["api"].get("concurrency", args.concurrency)))
    lock = threading.Lock()
    done = [0]

    def answer_question(q):
        reasoning1, answer1 = answer_turn(
            cfg, model, tokenizer, [{"role": "user", "content": q["turns"][0]}], think,
            prefilled, mode, prefill,
        )
        messages = [
            {"role": "user", "content": q["turns"][0]},
            assistant_message(answer1),
            {"role": "user", "content": q["turns"][1]},
        ]
        reasoning2, answer2 = answer_turn(
            cfg, model, tokenizer, messages, think, prefilled, mode, prefill
        )
        with lock:
            done[0] += 1
            empty = [t for t, a in ((1, answer1), (2, answer2)) if not a]
            note = f" (no answer on turn {', '.join(map(str, empty))})" if empty else ""
            print(f"{model_id}: question {q['question_id']} complete{note} [{done[0]}/{len(questions)}]", flush=True)
        return {
            "question_id": q["question_id"],
            "model_id": model_id,
            # `turns` holds the judged answers only; the reasoning traces are
            # archived alongside them and are never scored.
            "choices": [
                {
                    "index": 0,
                    "turns": [answer1, answer2],
                    "reasoning": [reasoning1, reasoning2],
                }
            ],
            "tstamp": time.time(),
        }

    print(f"{model_id}: generating {len(questions)} questions with {workers} workers", flush=True)
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(answer_question, questions))
    except Exception as error:
        if run_dir is not None:
            runs.update_stage(run_dir, "generate", "failed", error=repr(error))
        raise
    # Written in question order regardless of completion order, so the answer
    # file is byte-comparable across runs.
    with output.open("w") as fout:
        for row in rows:
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")
    empty = sum(1 for r in rows for t in r["choices"][0]["turns"] if not t.strip())
    if run_dir is not None:
        runs.update_stage(
            run_dir,
            "generate",
            "complete",
            questions=len(rows),
            turns=2 * len(rows),
            empty_answers=empty,
            api_mode=mode,
            prefill=prefill or None,
        )
    print(f"{model_id}: wrote {output} ({empty} empty answers of {2 * len(rows)} turns)")
    return run_dir


if __name__ == "__main__":
    main()
