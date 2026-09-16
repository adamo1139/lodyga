#!/usr/bin/env python3
"""Łodyga — one command to run a whole evaluation.

    ./lodyga.py run --config configs/config.poziomka.toml --judge configs/config.judge.toml

Generates answers, judges them, and aggregates the scores into a single
timestamped run directory, so the three stages can never describe different
runs. Individual stages remain reachable for re-judging or re-aggregating
existing results:

    ./lodyga.py judge --run-dir latest --judge configs/config.judge.toml
    ./lodyga.py aggregate --run-dir latest
    ./lodyga.py list

Works from any working directory: data files are resolved relative to this
file, not the shell's cwd.
"""

import argparse
import sys
from pathlib import Path

import runs

PROJECT_DIR = Path(__file__).resolve().parent


def _default_judge_config():
    for name in ("config.judge.toml", "judge.toml", "config.judge.example.toml"):
        for base in (PROJECT_DIR / "configs", PROJECT_DIR):
            path = base / name
            if path.exists():
                return path
    return None


def _stage_args(extra, **flags):
    """Build an argv list, dropping flags that are None/False."""
    argv = []
    for key, value in flags.items():
        if value is None or value is False:
            continue
        flag = "--" + key.replace("_", "-")
        argv.append(flag) if value is True else argv.extend([flag, str(value)])
    return argv + list(extra or [])


def _one_pass(args, judge_config, run_dir=None):
    """Generate, judge, and aggregate into a single run directory."""
    import aggregate_lodyga
    import generate_answers
    import judge_lodyga

    run_dir = generate_answers.main(
        _stage_args(None, config=args.config, run_dir=run_dir, concurrency=args.concurrency)
    )
    judge_lodyga.main(
        _stage_args(
            None, config=judge_config, run_dir=run_dir, concurrency=args.judge_concurrency
        )
    )
    aggregate_lodyga.main(
        _stage_args(None, run_dir=run_dir, iterations=args.iterations, seed=args.seed)
    )
    return run_dir


def cmd_run(args):
    judge_config = args.judge or _default_judge_config()
    if judge_config is None:
        sys.exit("error: no judge config found; pass --judge")

    passes = max(1, args.passes or 1)
    if passes == 1:
        run_dir = _one_pass(args, judge_config)
        _summarise(run_dir)
        return run_dir

    # Multi-pass: one parent directory holding a complete run per pass, plus a
    # summary. Generation is what is resampled; see custom_scoring.md.
    import tomllib

    model_id = tomllib.loads(Path(args.config).read_text())["model"]["id"]
    parent = runs.new_run_dir(f"{model_id}__{passes}pass")
    runs.archive_config(parent, "model", args.config)
    runs.archive_config(parent, "judge", judge_config)
    meta = runs.read_meta(parent)
    meta.update({"model_id": model_id, "passes": passes, "kind": "multipass"})
    runs.write_meta(parent, meta)
    print(f"multi-pass run: {parent} ({passes} passes)", flush=True)

    pass_dirs = []
    for index in range(1, passes + 1):
        print(f"\n===== pass {index}/{passes} =====", flush=True)
        pass_dir = parent / f"pass-{index}"
        pass_dir.mkdir()
        pass_dirs.append(_one_pass(args, judge_config, run_dir=pass_dir))
    _summarise_passes(parent, pass_dirs)
    return parent


def cmd_generate(args):
    import generate_answers

    run_dir = generate_answers.main(
        _stage_args(None, config=args.config, concurrency=args.concurrency)
    )
    print(f"\nnext: ./lodyga.py judge --run-dir {run_dir}")
    return run_dir


def cmd_judge(args):
    import judge_lodyga

    judge_config = args.judge or _default_judge_config()
    if judge_config is None:
        sys.exit("error: no judge config found; pass --judge")
    run_dir = judge_lodyga.main(
        _stage_args(
            None, config=judge_config, run_dir=args.run_dir, concurrency=args.judge_concurrency
        )
    )
    print(f"\nnext: ./lodyga.py aggregate --run-dir {run_dir}")
    return run_dir


def cmd_aggregate(args):
    import aggregate_lodyga

    run_dir = aggregate_lodyga.main(
        _stage_args(None, run_dir=args.run_dir, iterations=args.iterations, seed=args.seed)
    )
    _summarise(run_dir)
    return run_dir


def cmd_list(args):
    base = runs.RUNS_DIR
    if not base.is_dir():
        print(f"no runs yet ({base})")
        return
    entries = sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name)
    if not entries:
        print(f"no runs yet ({base})")
        return
    for path in entries[-args.limit :]:
        marker = " " if runs.is_complete(path) else "!"
        print(f"{marker} {runs.describe(path)}")


def _summarise_passes(parent, pass_dirs):
    """Mean across passes, with the two spreads kept separate.

    The per-pass bootstrap CI is uncertainty over questions within a pass; the
    across-pass range and standard deviation are run-to-run sampling variance.
    custom_scoring.md requires both to be reported and never merged.
    """
    import json
    import statistics

    entries = []
    for pass_dir in pass_dirs:
        meta = runs.read_meta(pass_dir)
        agg = meta.get("stages", {}).get("aggregate", {})
        gen = meta.get("stages", {}).get("generate", {})
        judge = meta.get("stages", {}).get("judge", {})
        entries.append(
            {
                "pass": Path(pass_dir).name,
                "score": agg.get("score"),
                "ci95": agg.get("ci95"),
                "scored_turns": agg.get("scored_turns"),
                "unscored_turns": agg.get("unscored_turns"),
                "empty_answers": gen.get("empty_answers"),
                "judge_model": judge.get("judge_model"),
            }
        )
    scores = [e["score"] for e in entries if e["score"] is not None]
    summary = {
        "protocol": runs.read_meta(parent).get("protocol", "Łodyga 0.1"),
        "passes": len(entries),
        "mean_score": statistics.fmean(scores) if scores else None,
        "score_range": [min(scores), max(scores)] if scores else None,
        # Sample stdev needs at least two passes; one pass has no spread.
        "score_stdev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        "per_pass": entries,
    }
    (parent / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")

    lines = [
        f"# Łodyga — wynik uśredniony z {len(entries)} przebiegów",
        "",
        f"**{summary['mean_score']:.2f}**  (średnia z {len(entries)} przebiegów)",
        "",
        f"- Rozrzut między przebiegami: {summary['score_range'][0]:.2f}–"
        f"{summary['score_range'][1]:.2f}, odchylenie standardowe "
        f"{summary['score_stdev']:.2f}",
        "- Przedziały ufności poniżej dotyczą pytań w obrębie jednego przebiegu"
        " i nie są tym samym co rozrzut między przebiegami.",
        "",
        "| Przebieg | Wynik | 95% CI (w przebiegu) | Tury ocenione | Bez oceny | Puste odpowiedzi |",
        "|---|---|---|---|---|---|",
    ]
    for e in entries:
        ci = f"[{e['ci95'][0]:.2f}, {e['ci95'][1]:.2f}]" if e.get("ci95") else "—"
        lines.append(
            f"| {e['pass']} | {e['score']:.2f} | {ci} | {e['scored_turns']} | "
            f"{e['unscored_turns']} | {e['empty_answers']} |"
        )
    (parent / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    meta = runs.read_meta(parent)
    meta["score"] = summary["mean_score"]
    runs.write_meta(parent, meta)
    for stage in runs.STAGES:
        runs.update_stage(parent, stage, "complete", passes=len(entries))

    print()
    print(f"multi-pass run: {parent}")
    print(f"  mean score   {summary['mean_score']:.2f}  over {len(entries)} passes")
    print(
        f"  spread       {summary['score_range'][0]:.2f}–{summary['score_range'][1]:.2f} "
        f"(sd {summary['score_stdev']:.2f})"
    )
    print(f"  per pass     {', '.join(f'{s:.2f}' for s in scores)}")
    print(f"  summary      {parent / 'summary.md'}")


def _summarise(run_dir):
    """Print the headline numbers a reader needs to judge whether a run is sound."""
    if run_dir is None:
        return
    meta = runs.read_meta(run_dir)
    stages = meta.get("stages", {})
    gen = stages.get("generate", {})
    judge = stages.get("judge", {})
    agg = stages.get("aggregate", {})
    print()
    print(f"run: {run_dir}")
    if agg.get("score") is not None:
        ci = agg.get("ci95") or [float("nan"), float("nan")]
        print(f"  score          {agg['score']:.2f}  95% CI [{ci[0]:.2f}, {ci[1]:.2f}]")
    if gen:
        print(f"  empty answers  {gen.get('empty_answers', '?')} of {gen.get('turns', '?')} turns")
    if judge:
        unscored = judge.get("unscored") or {}
        total_unscored = sum(unscored.values())
        detail = f" ({', '.join(f'{k}: {v}' for k, v in unscored.items())})" if unscored else ""
        print(f"  scored turns   {judge.get('scored', '?')}, unscored {total_unscored}{detail}")
    print(f"  report         {Path(run_dir) / 'report.md'}")


def build_parser():
    parser = argparse.ArgumentParser(prog="lodyga", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p, judge=False, aggregate=False, generate=False):
        if generate:
            p.add_argument("--config", type=Path, required=True, help="model config TOML")
            p.add_argument("--concurrency", type=int, help="questions generated at once")
        if judge:
            p.add_argument("--judge", type=Path, help="judge config TOML")
            p.add_argument("--judge-concurrency", type=int, help="turns judged at once")
        if aggregate:
            p.add_argument("--iterations", type=int, help="bootstrap iterations")
            p.add_argument("--seed", type=int, help="bootstrap seed")

    p_run = sub.add_parser("run", help="generate, judge, and aggregate in one go")
    add_common(p_run, generate=True, judge=True, aggregate=True)
    p_run.add_argument(
        "--passes",
        type=int,
        default=1,
        help="repeat the whole evaluation N times and average; default 1",
    )
    p_run.set_defaults(func=cmd_run)

    p_gen = sub.add_parser("generate", help="generate answers only")
    add_common(p_gen, generate=True)
    p_gen.set_defaults(func=cmd_generate)

    p_judge = sub.add_parser("judge", help="judge an existing run's answers")
    p_judge.add_argument("--run-dir", default="latest", help="run directory, or 'latest'")
    add_common(p_judge, judge=True)
    p_judge.set_defaults(func=cmd_judge)

    p_agg = sub.add_parser("aggregate", help="aggregate an existing run's judgments")
    p_agg.add_argument("--run-dir", default="latest", help="run directory, or 'latest'")
    add_common(p_agg, aggregate=True)
    p_agg.set_defaults(func=cmd_aggregate)

    p_list = sub.add_parser("list", help="list run directories, newest last")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
