# Polish MT-Bench

Local copy of the public Polish MT-Bench question set and the evaluation/browser
code published in the SpeakLeash Hugging Face Space.

## Contents

- `data/mt_bench/question.jsonl` — 80 Polish questions, each with two turns
  (160 generated responses per model). The file is about 60 kB.
- `data/mt_bench/mt-bench.csv` — upstream aggregate scores for reference models.
- `data/judge_prompts.jsonl` — the standard FastChat MT-Bench judge prompts.
- `generate_answers.py` — native-template renderer plus OpenAI-compatible
  `/v1/completions` generation runner.
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

## Generation runner

The project runner deliberately uses `/v1/completions`, not
`/v1/chat/completions`: it renders each model's own chat template locally with
`transformers`, then sends the resulting string to a vLLM-compatible server.
Turn 2 is rendered with turn 1 included as an assistant message. Responses are
cleaned of accidental end-of-turn markers before being inserted into the next
template, so chat-control tokens do not become conversational content.

```bash
python generate_answers.py --config config.example.toml
```

Copy the example to a model-specific TOML file and set the tokenizer path,
served model name, endpoint, and generation parameters. For a Hugging Face repo
whose tokenizer lives in a checkpoint subdirectory, set `tokenizer_subfolder`;
the runner downloads only that subdirectory and loads it locally.

## Łodyga: project-specific scoring

For the Poziomka comparison, use [`custom_scoring.md`](custom_scoring.md), which
defines the Łodyga benchmark, instead of the copied FastChat prompts. This
protocol uses every non-empty
reference field, including references on extraction, STEM, and role-play items.
It scores correctness, task completion, usefulness, and Polish presentation on
a 0–10 scale, reports both turns and all categories, and keeps Polish-language
rate separate from quality. It is a new evaluation and should not be presented
as a reproduced MT-Bench leaderboard result.
