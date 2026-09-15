#!/usr/bin/env python3
"""Run directories for Łodyga evaluations.

Every evaluation writes into its own timestamped directory and never touches a
previous one, so runs can be compared and a judgment file always sits next to
the exact answers it scored.

    data/mt_bench/runs/20260916T084500Z__poziomka_iter_0001718/
        answers.jsonl
        judgments.jsonl
        judgments__raw.jsonl
        aggregate.json
        report.md
        config.model.toml      copy of the model config actually used
        config.judge.toml      copy of the judge config actually used
        meta.json

`meta.json` carries a `status` per stage, so a run that died half way through is
identifiable instead of looking like a finished result.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# Paths are resolved against the project directory rather than the working
# directory, so the runners work from anywhere.
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data" / "mt_bench"
RUNS_DIR = DATA_DIR / "runs"
QUESTIONS = DATA_DIR / "question.jsonl"

STAGES = ("generate", "judge", "aggregate")


def _slug(text):
    """Filesystem-safe fragment of a model id."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", str(text)).strip("_") or "model"


def timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def new_run_dir(model_id, base=None):
    """Create and return a fresh run directory.

    The timestamp has one-second resolution, so a suffix is added in the
    unlikely case that two runs of the same model start in the same second.
    """
    base = Path(base) if base else RUNS_DIR
    stem = f"{timestamp()}__{_slug(model_id)}"
    path = base / stem
    suffix = 1
    while path.exists():
        suffix += 1
        path = base / f"{stem}-{suffix}"
    path.mkdir(parents=True)
    return path


def latest_run_dir(base=None):
    """Most recent run directory, or None. Names sort chronologically."""
    base = Path(base) if base else RUNS_DIR
    if not base.is_dir():
        return None
    dirs = sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name)
    return dirs[-1] if dirs else None


def resolve_run_dir(value, base=None):
    """Accept a path or the literal 'latest'."""
    if value in (None, "latest"):
        run_dir = latest_run_dir(base)
        if run_dir is None:
            raise SystemExit("error: no run directories found; generate answers first")
        return run_dir
    path = Path(value)
    if not path.is_dir():
        raise SystemExit(f"error: run directory not found: {path}")
    return path


def answers_path(run_dir):
    return Path(run_dir) / "answers.jsonl"


def judgments_path(run_dir):
    return Path(run_dir) / "judgments.jsonl"


def meta_path(run_dir):
    return Path(run_dir) / "meta.json"


def read_meta(run_dir):
    path = meta_path(run_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def write_meta(run_dir, meta):
    """Write meta.json atomically so an interrupted write cannot truncate it."""
    path = meta_path(run_dir)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, path)


def update_stage(run_dir, stage, status, **fields):
    """Record the outcome of one stage in meta.json.

    `status` is 'running', 'complete', or 'failed'. A run whose meta shows no
    'complete' aggregate stage is incomplete, whatever files happen to exist.
    """
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}")
    meta = read_meta(run_dir)
    stages = meta.setdefault("stages", {})
    entry = stages.setdefault(stage, {})
    entry["status"] = status
    entry.update(fields)
    if status == "running":
        entry["started"] = entry.get("started") or datetime.now(timezone.utc).isoformat()
    else:
        entry["finished"] = datetime.now(timezone.utc).isoformat()
    write_meta(run_dir, meta)
    return meta


def archive_config(run_dir, kind, config_path):
    """Copy a config file into the run directory verbatim.

    custom_scoring.md requires the configs used to be archived with results;
    copying the bytes means a later edit to the working config cannot rewrite
    history.
    """
    if config_path is None:
        return None
    target = Path(run_dir) / f"config.{kind}.toml"
    target.write_text(Path(config_path).read_text())
    return target.name


def is_complete(run_dir):
    """True only when every stage finished and none failed.

    Checking the aggregate stage alone is not enough: a re-judge that fails
    after a successful aggregate would otherwise leave the run looking sound.
    """
    stages = read_meta(run_dir).get("stages", {})
    return all(stages.get(stage, {}).get("status") == "complete" for stage in STAGES)


def describe(run_dir):
    """One-line summary of a run directory, for listings."""
    meta = read_meta(run_dir)
    stages = meta.get("stages", {})
    done = [s for s in STAGES if stages.get(s, {}).get("status") == "complete"]
    failed = [s for s in STAGES if stages.get(s, {}).get("status") == "failed"]
    score = meta.get("score")
    parts = [Path(run_dir).name]
    if score is not None:
        parts.append(f"score {score:.2f}")
    parts.append("stages: " + (",".join(done) if done else "none"))
    if failed:
        parts.append("FAILED: " + ",".join(failed))
    return "  ".join(parts)
