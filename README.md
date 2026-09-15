# Łodyga — Polish MT-Bench

Evaluates Polish chat models on 80 two-turn questions. The protocol — rubric,
judge prompts, passes, aggregation, language ID — is in
[`custom_scoring.md`](custom_scoring.md). A new evaluation, not a reproduction of
the SpeakLeash leaderboard.

```bash
cp .env.example .env && chmod 600 .env    # add OPENROUTER_API_KEY
./lodyga.py run --config config.poziomka.toml --judge config.judge.example.toml
```

Copy `config.example.toml` per model. `run` generates, judges and scores into a
timestamped directory under `data/mt_bench/runs/` holding the answers, judgments,
raw judge archive, report and configs used; nothing is overwritten. `--passes N`
averages repeated runs. See `./lodyga.py --help`.

Questions: [speakleash/mt-bench-pl](https://huggingface.co/spaces/speakleash/mt-bench-pl),
MT-Bench translated to Polish, upstream `license: other` — check terms before
redistributing. `app.py`, `common.py`, `content.py`, `src/` are unused upstream code.
