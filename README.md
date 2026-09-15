# Polish MT-Bench

Local copy of the public Polish MT-Bench question set and the evaluation/browser
code published in the SpeakLeash Hugging Face Space.

## Contents

- `data/mt_bench/question.jsonl` — 80 Polish questions, each with two turns
  (160 generated responses per model). The file is about 60 kB.
- `data/mt_bench/mt-bench.csv` — upstream aggregate scores for reference models.
- `data/judge_prompts.jsonl` — the standard FastChat MT-Bench judge prompts.
- `lodyga.py` — single entry point: `run`, `generate`, `judge`, `aggregate`,
  `list`.
- `generate_answers.py` — native-template renderer plus OpenAI-compatible
  `/v1/completions` generation runner.
- `judge_lodyga.py`, `aggregate_lodyga.py` — judge runner and score aggregation.
- `runs.py` — timestamped run directories and per-stage run metadata.
- `config.example.toml` — zero-dependency TOML configuration example.
- `common.py`, `app.py`, `content.py`, and `src/` — copied upstream utilities,
  leaderboard UI, and answer/judgment browser code.
- `requirements.txt` — the upstream UI requirements.

The large upstream `model_answer/` and `model_judgment/` archives are not copied;
they are reference results rather than inputs needed to evaluate a new model.

## Upstream and provenance

- Space: <https://huggingface.co/spaces/speakleash/mt-bench-pl>
- Questions: <https://huggingface.co/spaces/speakleash/mt-bench-pl/blob/main/data/mt_bench/question.jsonl>
- Original Polish dataset mirror: <https://huggingface.co/datasets/lightblue/mt_bench_polish>
- Judge prompt source: <https://github.com/lm-sys/FastChat/blob/main/fastchat/llm_judge/data/judge_prompts.jsonl>

The Polish questions were translated from MT-Bench and corrected by a Polish
speaker. The upstream Space metadata uses `license: other`; public availability
should not be interpreted as an unrestricted redistribution license. Keep this
provenance with results and check the upstream terms before publishing the
questions elsewhere.

## What can be reused

The question file is directly reusable for generation. The copied `common.py`
contains the upstream single-answer and pairwise judging logic, and
`data/judge_prompts.jsonl` restores the standard prompt definitions, but this is
still not a standalone evaluator:

- it expects FastChat conversation templates and the old OpenAI/Anthropic client
  APIs;
- the answer-generation scripts are not in this Space checkout;
- `app.py` is a browser for already-generated answers and judgments, not a local
  Hugging Face inference runner.

For this project, generate one JSONL answer file per model using the model's
native chat template, then use the public questions as input to a fixed judge
script. Preserve both raw answer files and judge outputs. A sensible comparison
is all 80 questions, both turns, identical generation limits, and one fixed
judge model/seed for Poziomka, Polanka, and Bielik.

The question file has `reference` fields on 40 of 80 questions. The upstream
judge logic treats only `math`, `reasoning`, and `coding` as reference-based;
references attached to extraction, STEM, and role-play questions are ignored by
that logic. Decide and document whether to preserve this behavior.

The upstream code is retained here as a reference and can be adapted if the
FastChat dependencies and judge prompt configuration are restored.

## Running an evaluation

`lodyga.py` runs the whole pipeline — generate, judge, aggregate — into a single
timestamped run directory, so the three stages can never describe different
runs:

```bash
cp .env.example .env && chmod 600 .env   # then fill in OPENROUTER_API_KEY
./lodyga.py run --config config.poziomka.toml --judge config.judge.toml
```

It prints the headline score, the empty-answer count, and the unscored count.
Other subcommands:

```bash
./lodyga.py run --config … --judge … --passes 5   # average N passes, with spread
./lodyga.py judge --run-dir latest --judge …      # re-judge without regenerating
./lodyga.py aggregate --run-dir latest            # re-score existing judgments
./lodyga.py list                                  # all runs, newest last
```

Each run lands in `data/mt_bench/runs/<UTC timestamp>__<model_id>/` holding
`answers.jsonl`, `judgments.jsonl`, `judgments__raw.jsonl`, `aggregate.json`,
`report.md`, `meta.json`, and verbatim copies of both configs used. Nothing is
ever overwritten, and `meta.json` records each stage as running, complete, or
failed, so an interrupted run cannot be mistaken for a finished one. Run
directories are gitignored: results are reproducible from the archived configs
rather than version-controlled.

The three stage scripts below remain usable directly; the sections describe
what each one does.

## Generation runner

The project runner deliberately uses `/v1/completions`, not
`/v1/chat/completions`: it renders each model's own chat template locally with
`transformers`, then sends the resulting token-ID list to a SGLang/vLLM-compatible
server. This avoids server-side BOS insertion or a second chat-template pass.
Turn 2 is rendered with turn 1 included as an assistant message. Responses are
cleaned of accidental end-of-turn markers before being inserted into the next
template, so chat-control tokens do not become conversational content.

For thinking models the reasoning trace is split from the answer at `</think>`
and kept out of both the score and the conversation: `choices[0].turns` holds
the judged answers, `choices[0].reasoning` archives the traces, and turn 2 sees
only the turn-1 answer — the trace is dropped from its context even where the
chat template would preserve it. A model that never closes its reasoning block
produced no answer, and the empty answer is recorded rather than replaced by
the trace.

```bash
python generate_answers.py --config config.example.toml
```

Copy the example to a model-specific TOML file and set the tokenizer path,
served model name, endpoint, and generation parameters. Set `api.model` to the
name the endpoint serves; leaving it empty falls back to one `/models` query at
startup. For a Hugging Face repo whose tokenizer lives in a checkpoint
subdirectory, set `tokenizer_subfolder`; the runner downloads only that
subdirectory and loads it locally. Each run rewrites the answer file in full —
there is no resume.

## Łodyga: project-specific scoring

For the Poziomka comparison, use [`custom_scoring.md`](custom_scoring.md), which
defines the Łodyga benchmark, instead of the copied FastChat prompts. This
protocol uses every non-empty
reference field, including references on extraction, STEM, and role-play items.
It scores correctness, task completion, usefulness, and Polish presentation on
a 0–10 scale, reports both turns and all categories, and keeps Polish-language
rate separate from quality. It is a new evaluation and should not be presented
as a reproduced MT-Bench leaderboard result.

## Judge runner

`judge_lodyga.py` scores an answer file against the frozen Łodyga 0.1 protocol:
one judge call per turn through an OpenAI-compatible chat-completions API
(OpenRouter), the prompts from `custom_scoring.md`, per-turn references, strict
JSON validation (invalid JSON, out-of-range scores, or a mismatched total are
recorded as `unscored` with a reason — never retried, never imputed), and raw
request/response archiving.

```bash
# judge config copies config.judge.example.toml; sampling is frozen per run
OPENROUTER_API_KEY=... python judge_lodyga.py \
    --config config.judge.toml \
    --run-dir latest
```

Keys can also go in a `.env` file: `cp .env.example .env && chmod 600 .env`,
then fill in `OPENROUTER_API_KEY`. `.env` is gitignored and never committed;
`.env.example` is the committed template and holds no key material. `.env` is
read from the project directory, so the runners find the key from any working
directory, and a real environment variable always wins over the file. Outputs land in
`data/mt_bench/model_judgment/<judge>/<model>.jsonl` (one row per judged turn,
scored or unscored), plus `<model>__raw.jsonl` and `<model>__meta.json`.
Questions with no answer row are skipped. There is no resume: every run judges
the whole answer file and rewrites all three outputs, so a judgment file always
describes exactly one complete run and its meta summary always matches it. The
meta file archives the judge config, protocol version, and the scored/unscored
summary; aggregation over the judgment rows is handled separately.

## Aggregation

`aggregate_lodyga.py` turns a judgment file into results per the Łodyga 0.1
aggregation rules: the headline score is the arithmetic mean of all scored
turn totals; turn-1, turn-2, the eight category means, and
reference-vs-no-reference means are reported with bootstrap 95% confidence
intervals (questions resampled, both turns kept together). Unscored turns are
excluded and reported separately — never imputed. The share of answers
classified as Polish is computed from the answer text with a documented
heuristic (Polish diacritics or distinctive Polish function words) and
reported only as a descriptor, never as a score multiplier.

```bash
python aggregate_lodyga.py --run-dir latest
```

Two files are written next to the judgment file: `<model>__aggregate.json`
(machine-readable: means, CIs, dimension averages, Polish rate, and a
per-question breakdown) and `<model>__report.md` (human-readable). Bootstrap
iterations and seed default to 10000 and 12345 and can be overridden with
`--iterations` and `--seed`; the values used are recorded in the output.
