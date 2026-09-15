#!/usr/bin/env python3
"""Aggregate Łodyga judgments into machine- and human-readable results.

Implements the aggregation rules from custom_scoring.md (Łodyga 0.1): the
headline score is the arithmetic mean of all scored turn totals; turn-1,
turn-2, eight category, and reference-vs-no-reference means are also reported;
bootstrap 95% confidence intervals are computed over questions, resampling
both turns of a question together. Unscored turns are never imputed — they are
excluded from means and reported separately. The share of answers identified as
Polish (OpenLID v3) is reported as a separate descriptive statistic and never
affects a score.
"""

import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import runs

PROTOCOL = "Łodyga 0.1"

CATEGORY_LABELS = {
    "writing": "Piśmiennictwo",
    "roleplay": "Odgrywanie ról",
    "reasoning": "Wnioskowanie",
    "math": "Matematyka",
    "coding": "Kodowanie",
    "extraction": "Ekstrakcja",
    "stem": "Nauki ścisłe",
    "humanities": "Humanistyka",
}

# Language identification uses OpenLID v3 (HPLT), a fastText classifier over
# ~200 languages. It replaces an earlier diacritics-and-function-words
# heuristic, which could not recognise Polish written without diacritics and
# could not tell prose from a CSV dump.
OPENLID_REPO = "HPLT/OpenLID-v3"
OPENLID_FILE = "openlid-v3.bin"
# Labels counted as Polish. Silesian (szl_Latn) is included deliberately: it is
# close enough to Polish that OpenLID splits its probability between the two on
# ordinary Polish text — the one case observed was a JSON array of Polish place
# names scored szl 0.57 / pol 0.20. Counting it as a different language would
# report a language failure where there is none.
POLISH_LABELS = ("pol_Latn", "szl_Latn")
# Below this probability the classifier is not making a usable claim, so the
# answer is reported as undetermined rather than silently counted as non-Polish.
MIN_CONFIDENCE = 0.5
# "No linguistic content" — tables, code, bare numbers. Not a language failure,
# so it is reported in its own bucket.
NO_CONTENT_LABEL = "zxx_Zxxx"

_MODEL = None


def load_language_model(path=None):
    """Load OpenLID v3 once, from the local HF cache when available."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    import fasttext

    if path is None:
        from huggingface_hub import hf_hub_download

        path = hf_hub_download(OPENLID_REPO, OPENLID_FILE)
    _MODEL = fasttext.load_model(str(path))
    return _MODEL


def detect_language(text, model, k=1):
    """Return the top-k [(label, probability)] for one answer.

    fastText reads a single line, so newlines are flattened; they carry no
    language information anyway.
    """
    flattened = " ".join(text.split())
    if not flattened:
        return []
    labels, probs = model.predict(flattened, k=k)
    return [(l.removeprefix("__label__"), float(p)) for l, p in zip(labels, probs)]


def classify_language(text, model):
    """Bucket one answer: 'empty', 'polish', 'other', 'no_content', or
    'undetermined'.

    'empty' is kept apart from 'undetermined': an answer the model never
    produced is a generation failure, not a language the detector could not
    identify. Descriptive only — no bucket affects any score.
    """
    if not text.strip():
        return "empty", None, 0.0
    ranked = detect_language(text, model, k=5)
    if not ranked:
        return "undetermined", None, 0.0
    label, prob = ranked[0]
    # Polish and Silesian are counted together, so text whose probability mass
    # is split between them is not pushed below the threshold by the split
    # itself.
    polish_mass = sum(p for name, p in ranked if name in POLISH_LABELS)
    if polish_mass >= MIN_CONFIDENCE:
        return "polish", POLISH_LABELS[0], polish_mass
    if prob < MIN_CONFIDENCE:
        return "undetermined", label, prob
    if label == NO_CONTENT_LABEL:
        return "no_content", label, prob
    return "other", label, prob


def per_turn_reference(question):
    """Which turns of a question showed a reference in the judge prompt.

    Turn 1 shows a reference when its first list entry is non-empty; turn 2
    shows one when either entry is non-empty (matching judge_lodyga.py).
    """
    ref = question.get("reference")
    if not isinstance(ref, list):
        return False, False
    ref0 = bool(ref and len(ref) > 0 and str(ref[0]).strip())
    ref1 = bool(len(ref) > 1 and str(ref[1]).strip())
    return ref0, ref0 or ref1


def load_judgments(path):
    scored = {}
    unscored = defaultdict(int)
    meta = {"model_id": None, "judge_model": None}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if meta["model_id"] is None:
            meta["model_id"] = row.get("model_id")
        if meta["judge_model"] is None:
            meta["judge_model"] = row.get("judge_model")
        key = (row["question_id"], row["turn"])
        if row.get("status") == "scored":
            scored[key] = row["judgment"]
        else:
            unscored[row.get("reason", "unscored")] += 1
    return scored, dict(unscored), meta


def load_questions(path):
    questions = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        q = json.loads(line)
        ref_turn1, ref_turn2 = per_turn_reference(q)
        questions[q["question_id"]] = {
            "category": q.get("category"),
            "reference_turn1": ref_turn1,
            "reference_turn2": ref_turn2,
        }
    return questions


def load_answers(path):
    answers = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        turns = row.get("choices", [{}])[0].get("turns", [])
        if len(turns) == 2:
            answers[row["question_id"]] = turns
    return answers


def percentile(sorted_values, p):
    """Nearest-rank percentile of an already sorted list."""
    if not sorted_values:
        return None
    return sorted_values[min(len(sorted_values) - 1, round(p / 100.0 * (len(sorted_values) - 1)))]


def metric(pool, rng, iterations):
    """Bootstrap statistics for a pool of questions -> scored turn totals."""
    totals_by_q = [(qid, totals) for qid, totals in pool.items()]
    all_totals = [t for _, totals in totals_by_q for t in totals]
    if not all_totals:
        return None
    samples = []
    n = len(totals_by_q)
    for _ in range(iterations):
        totals = []
        for _ in range(n):
            totals.extend(totals_by_q[rng.randrange(n)][1])
        if totals:
            samples.append(sum(totals) / len(totals))
    samples.sort()
    return {
        "mean": sum(all_totals) / len(all_totals),
        "ci95": [percentile(samples, 2.5), percentile(samples, 97.5)],
        "n_questions": n,
        "n_turns": len(all_totals),
    }


def build_pool(qids, scored, turn=None, ref_filter=None, ref_shown=None):
    """Group scored turn totals by question, optionally restricted to one turn
    or to turns whose reference presence matches `ref_filter`."""
    pool = {}
    for qid in qids:
        totals = []
        for turn_idx in (1, 2):
            if turn is not None and turn_idx != turn:
                continue
            if ref_filter is not None and ref_shown(qid, turn_idx) != ref_filter:
                continue
            judgment = scored.get((qid, turn_idx))
            if judgment is not None:
                totals.append(judgment["total"])
        if totals:
            pool[qid] = totals
    return pool


def render_report(result):
    def fmt(stats):
        if stats is None:
            return "—"
        ci = f"[{stats['ci95'][0]:.2f}, {stats['ci95'][1]:.2f}]"
        return f"{stats['mean']:.2f} ({stats['n_turns']} tur, {stats['n_questions']} pytań)" \
            f"  95% CI {ci}"

    lines = [
        f"# Łodyga — wyniki ({result['protocol']})",
        "",
        f"- Model: {result['model_id']} · Sędzia: {result['judge_model']}",
        f"- Oceny: `{result['judgments_file']}`",
        f"- Bootstrap: {result['bootstrap_iterations']} iteracji, seed {result['seed']} "
        "(resampling pytań z zachowaniem obu tur razem)",
        (
            f"- Tury ocenione: {result['n_scored_turns']} · "
            f"Tury bez oceny: {result['n_unscored_turns']}"
        ),
        "",
        "## Wynik ogólny (średnia arytmetyczna wszystkich ocenionych tur)",
        "",
        f"**{result['overall']['mean']:.2f}**  ({result['overall']['n_turns']} tur, "
        f"{result['overall']['n_questions']} pytań; 95% CI "
        f"[{result['overall']['ci95'][0]:.2f}, {result['overall']['ci95'][1]:.2f}])",
        "",
        "## Średnie wg metryki",
        "",
        "| Metryka | Średnia |",
        "|---|---|",
    ]
    labels = {"1": "Tura 1", "2": "Tura 2"}
    for key, stats in result["by_turn"].items():
        lines.append(f"| {labels.get(key, key)} | {fmt(stats)} |")
    lines.append("")
    lines.append("## Średnie wg kategorii")
    lines.append("")
    lines.append("| Kategoria | Średnia |")
    lines.append("|---|---|")
    for cat, stats in result["by_category"].items():
        lines.append(f"| {CATEGORY_LABELS.get(cat, cat)} | {fmt(stats)} |")
    lines.append("")
    lines.append("## Odniesienia (z / bez referencji)")
    lines.append("")
    lines.append("| Grupa | Średnia |")
    lines.append("|---|---|")
    lines.append(f"| z referencją | {fmt(result['by_reference']['reference'])} |")
    lines.append(f"| bez referencji | {fmt(result['by_reference']['no_reference'])} |")
    lines.append("")
    lines.append("## Średnie wymiarów (na ocenioną turę)")
    lines.append("")
    for name, value in result["dimensions"].items():
        lines.append(f"- **{name}**: {value:.2f}")
    lines.append("")
    lines.append("## Odsetek odpowiedzi w języku polskim")
    lines.append("")
    if result["polish_rate"] is None:
        lines.append("Nie wyliczono (brak pliku odpowiedzi lub wyłączona detekcja języka).")
    else:
        buckets = result.get("language_buckets", {})
        total = sum(buckets.values()) or 1
        lines.append(
            f"**{result['polish_rate'] * 100:.1f}%** odpowiedzi rozpoznano jako polskie "
            f"(detektor: {result.get('language_detector')}, próg pewności "
            f"{result.get('language_min_confidence')}; statystyka opisowa, "
            "nie czynnik mnożący wynik)."
        )
        lines.append("")
        lines.append("| Klasyfikacja | Tury | Udział |")
        lines.append("|---|---:|---:|")
        labels = {
            "polish": "polski",
            "other": "inny język",
            "no_content": "brak treści językowej (tabele, kod, liczby)",
            "empty": "pusta odpowiedź (model nic nie wygenerował)",
            "undetermined": f"nierozstrzygnięte (pewność < {result.get('language_min_confidence')})",
        }
        for key, label in labels.items():
            count = buckets.get(key, 0)
            lines.append(f"| {label} | {count} | {count / total * 100:.1f}% |")
        others = result.get("other_languages") or {}
        if others:
            detail = ", ".join(f"{lang}: {n}" for lang, n in sorted(others.items()))
            lines.append("")
            lines.append(f"Wykryte inne języki — {detail}.")
    lines.append("")
    lines.append("## Tury bez oceny")
    lines.append("")
    unscored = result["unscored_reasons"]
    if unscored:
        for reason, count in unscored.items():
            lines.append(f"- {reason}: {count}")
    else:
        lines.append("Brak.")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        help="run directory to aggregate, or 'latest'; judgments and answers live there",
    )
    parser.add_argument(
        "--judgments",
        type=Path,
        help="judgments JSONL to aggregate instead of a run directory's judgments.jsonl",
    )
    parser.add_argument(
        "--questions",
        type=Path,
        default=runs.QUESTIONS,
        help="Łodyga question file (provides categories and references)",
    )
    parser.add_argument(
        "--answers",
        type=Path,
        help="answers JSONL from generate_answers.py (for the Polish-language rate)",
    )
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--language-model",
        type=Path,
        help="path to the OpenLID v3 .bin; downloaded from the HF cache by default",
    )
    parser.add_argument(
        "--no-language-detection",
        action="store_true",
        help="skip language identification (avoids loading the 1.2 GB model)",
    )
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=12345)
    args = parser.parse_args(argv)
    if not args.judgments and not args.run_dir:
        parser.error("one of --run-dir or --judgments is required")

    run_dir = None
    judgments = args.judgments
    answers_file = args.answers
    if args.run_dir or not args.judgments:
        run_dir = runs.resolve_run_dir(args.run_dir)
        judgments = args.judgments or runs.judgments_path(run_dir)
        if not judgments.exists():
            raise SystemExit(f"error: no judgments in {run_dir}; judge the run first")
        # The answers next to the judgments are the ones that were judged, so
        # the Polish-language rate cannot be computed from a mismatched file.
        if answers_file is None and runs.answers_path(run_dir).exists():
            answers_file = runs.answers_path(run_dir)
        runs.update_stage(run_dir, "aggregate", "running")

    scored, unscored, meta = load_judgments(judgments)
    questions = load_questions(args.questions)
    answers = load_answers(answers_file) if answers_file else {}

    if not scored:
        if run_dir is not None:
            runs.update_stage(run_dir, "aggregate", "failed", error="no scored turns")
        raise SystemExit(f"error: no scored turns in {judgments}")

    rng = random.Random(args.seed)
    qids = list(questions)

    def ref_shown(qid, turn):
        info = questions[qid]
        return info["reference_turn1"] if turn == 1 else info["reference_turn2"]

    overall = metric(build_pool(qids, scored), rng, args.iterations)
    by_turn = {
        str(t): metric(build_pool(qids, scored, turn=t), rng, args.iterations)
        for t in (1, 2)
    }
    categories = {}
    for qid, info in questions.items():
        categories.setdefault(info["category"], []).append(qid)
    by_category = {
        cat: metric(build_pool(cat_qids, scored), rng, args.iterations)
        for cat, cat_qids in sorted(categories.items())
    }
    by_reference = {
        "reference": metric(
            build_pool(qids, scored, ref_filter=True, ref_shown=ref_shown), rng, args.iterations
        ),
        "no_reference": metric(
            build_pool(qids, scored, ref_filter=False, ref_shown=ref_shown), rng, args.iterations
        ),
    }

    dimensions = {name: 0.0 for name in ("correctness", "task_completion", "usefulness", "polish")}
    for judgment in scored.values():
        for name in dimensions:
            dimensions[name] += judgment[name]
    n_dim = len(scored)
    dimensions = {name: value / n_dim for name, value in dimensions.items()}

    polish_rate = None
    language_buckets = defaultdict(int)
    other_languages = defaultdict(int)
    n_total = 0
    if answers and not args.no_language_detection:
        model = load_language_model(args.language_model)
        for qid, turns in answers.items():
            for turn_idx, text in enumerate(turns, start=1):
                if (qid, turn_idx) not in scored:
                    continue
                n_total += 1
                bucket, label, _ = classify_language(text, model)
                language_buckets[bucket] += 1
                if bucket == "other":
                    other_languages[label] += 1
        if n_total:
            # Share of Polish among all scored answers. 'no_content' and
            # 'undetermined' stay in the denominator and are reported
            # separately, so the number is never quietly flattered.
            polish_rate = language_buckets["polish"] / n_total

    detail = []
    for qid in qids:
        info = questions[qid]
        turns = {}
        for t in (1, 2):
            if (qid, t) in scored:
                turns[str(t)] = {"status": "scored", "total": scored[(qid, t)]["total"]}
            else:
                turns[str(t)] = {"status": "unscored"}
        detail.append(
            {
                "question_id": qid,
                "category": info["category"],
                "reference_turn1": info["reference_turn1"],
                "reference_turn2": info["reference_turn2"],
                "turns": turns,
            }
        )

    result = {
        "protocol": PROTOCOL,
        "judgments_file": str(judgments),
        "questions_file": str(args.questions),
        "answers_file": str(answers_file) if answers_file else None,
        "model_id": meta["model_id"],
        "judge_model": meta["judge_model"],
        "seed": args.seed,
        "bootstrap_iterations": args.iterations,
        "generated": time.time(),
        "overall": overall,
        "by_turn": by_turn,
        "by_category": by_category,
        "by_reference": by_reference,
        "dimensions": dimensions,
        "polish_rate": polish_rate,
        "language_detector": None if args.no_language_detection else OPENLID_REPO,
        "language_min_confidence": MIN_CONFIDENCE,
        "language_buckets": dict(language_buckets),
        "other_languages": dict(other_languages),
        "n_questions": len(qids),
        "n_scored_turns": len(scored),
        "n_unscored_turns": sum(unscored.values()),
        "unscored_reasons": unscored,
        "questions": detail,
    }

    if run_dir is not None:
        default_json = Path(run_dir) / "aggregate.json"
        default_report = Path(run_dir) / "report.md"
    else:
        default_json = judgments.with_name(judgments.stem + "__aggregate.json")
        default_report = judgments.with_name(judgments.stem + "__report.md")
    output_json = args.output_json or default_json
    report = args.report or default_report
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    report.write_text(render_report(result), encoding="utf-8")

    print(
        f"overall mean {overall['mean']:.2f} 95% CI "
        f"[{overall['ci95'][0]:.2f}, {overall['ci95'][1]:.2f}] "
        f"({overall['n_turns']} scored turns, {overall['n_questions']} questions)"
    )
    print(f"wrote {output_json}")
    print(f"wrote {report}")
    if run_dir is not None:
        meta_file = runs.read_meta(run_dir)
        meta_file["score"] = overall["mean"]
        runs.write_meta(run_dir, meta_file)
        runs.update_stage(
            run_dir,
            "aggregate",
            "complete",
            score=overall["mean"],
            ci95=overall["ci95"],
            scored_turns=overall["n_turns"],
            unscored_turns=result["n_unscored_turns"],
        )
    return run_dir


if __name__ == "__main__":
    main()