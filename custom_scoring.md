# Łodyga — scoring benchmarku rozmów wieloetapowych

Łodyga is the project-specific evaluation built from the public Polish MT-Bench
questions. It is intentionally not claimed to reproduce the SpeakLeash
leaderboard.

## Versioning

This document defines **Łodyga 0.1**, frozen on 2026-09-15. The question set,
the reference policy, the rubric, the judge prompts, and the aggregation rules
below are fixed for the 0.1 release. The judge model and its sampling are set
in the judge config file, and each model's generation settings live in that
model's own config file; both files are archived with every run. Any change to
the frozen parts requires a version bump (0.2, …) and a full re-run of every
model; published results must always state the protocol version and the config
files they were produced with.

## What is scored

Each model answers all 80 questions, including both turns. Turn 2 is judged with
the full conversation visible, including the model's turn-1 answer. Each turn is
scored independently on a 0–10 scale:

| Dimension | Points | Meaning |
|---|---:|---|
| Correctness and factuality | 0–4 | The answer is true, logically sound, and technically correct. |
| Task completion | 0–3 | It follows the requested operation, constraints, and follow-up. |
| Usefulness and completeness | 0–2 | It addresses the user's need with enough relevant detail. |
| Polish and presentation | 0–1 | Natural Polish, readable structure, and clear final answer. |

The judge must not reward length by itself. Deduct for repetition, irrelevant
digressions, unusable formatting, or an answer that contradicts itself.

## Reasoning traces are never judged

For a thinking model, only the final answer is scored. The reasoning trace is
separated from the answer at generation time, archived next to it, and never
sent to the judge — so no model is rewarded or penalised for how much it thought,
and the Polish-language statistic describes the answer rather than the trace.

The split is the text after the model closes its reasoning block with
`</think>`. If the model never closes the block, it produced no answer within
its token budget: the answer is recorded as empty and scored as such. The trace
is never promoted to an answer.

## References

Use every non-empty `reference` supplied in `question.jsonl`, regardless of
category. A reference is evidence about the expected answer, not an instruction
to copy its wording. If a reference is incomplete, ambiguous, or appears wrong,
the judge should rely on the question and domain knowledge and mention that in
the explanation.

## Answer generation

- One answer file per model, covering all 80 questions and both turns
  (160 answers per model). Each answer row carries the judged answers in
  `choices[0].turns` and the matching reasoning traces in
  `choices[0].reasoning`; only `turns` is ever scored.
- Turn 2 is generated with the visible conversation in context: question 1, the
  model's own turn-1 **answer**, and question 2. The turn-1 reasoning trace is
  dropped from that context even when the model's chat template would preserve
  it, so the follow-up is answered from what a user would actually see. Turn 2
  still reasons freshly; the discarded trace remains archived in the answer
  file.
- Each model is run from its own config file that specifies the model, its
  chat template, and its generation settings (sampling parameters and token
  limits). There is no protocol-wide token limit and no cross-model sampling
  requirement; the config file used is recorded in run metadata.

## Judge

- The judge is called through the **OpenRouter** chat-completions API. The
  judge model and its sampling are set in the judge config file. Which sampling
  knobs exist depends on the judge: a reasoning model such as
  `openai/gpt-5.6-luna` takes `seed`, `max_tokens`, and `reasoning_effort` but
  rejects `temperature` and `top_p`, so only parameters the model actually
  supports may be listed. Whatever is set is frozen for the whole run — the same
  values apply to every judged turn — and the config file is archived with the
  results.
- Łodyga 0.1 runs the judge with `reasoning_effort = "none"`: the judge scores
  directly from the rubric prompt without a reasoning pass. This is recorded in
  the archived config, and `max_tokens` therefore only has to cover the rubric
  JSON. A judge that exhausts its budget before closing the JSON returns
  unusable content, and that turn is recorded as unscored like any other invalid
  output.
- API keys are loaded from `.env` and are never hardcoded or committed.
- The judge prompt is sent as a single user message built from the templates
  below. When a question has no non-empty `reference`, the reference block is
  omitted from the prompt entirely; it is never substituted with an empty
  string.
- The judge must return exactly the JSON object described in the rubric, and
  `total` must equal the sum of the four dimensions. There are no retries: a
  response with invalid JSON, out-of-range scores, or a mismatched total is
  recorded as unscored in run metadata and reported separately; scores are
  never imputed.
- Raw judge requests and responses are archived for every run.

## Judge prompt: first turn

Use this template, substituting the question, optional reference, and answer:

```text
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
 "total": 0, "explanation": "krótkie uzasadnienie po polsku"}

PYTANIE:
{question}

REFERENCJA (opcjonalna; traktuj ją jako wskazówkę, nie jako tekst do kopiowania):
{reference}

ODPOWIEDŹ ASYSTENTA:
{answer}
```

## Judge prompt: second turn

Use the same rubric, but show the complete two-turn exchange and explicitly score
the answer to the follow-up:

```text
Oceń przede wszystkim odpowiedź na DRUGIE pytanie, uwzględniając pierwsze pytanie
oraz pierwszą odpowiedź jako kontekst. Sprawdź, czy asystent rzeczywiście wykonał
zmianę, korektę lub dodatkowe zadanie z drugiego pytania. Zastosuj dokładnie te same
cztery wymiary i zwróć wyłącznie ten sam format JSON.

PIERWSZE PYTANIE:
{question_1}

PIERWSZA ODPOWIEDŹ:
{answer_1}

REFERENCJA DO PIERWSZEGO PYTANIA (opcjonalna):
{reference_1}

DRUGIE PYTANIE:
{question_2}

REFERENCJA (opcjonalna):
{reference_2}

DRUGA ODPOWIEDŹ — OCENIANA:
{answer_2}
```

## Passes

A single generation pass is one sample of a sampling model, so a score from one
pass confounds model quality with sampling luck. An evaluation may therefore run
`N` passes and report their mean as the headline score.

- **Generation is what is resampled.** Each pass regenerates all 160 turns and
  judges them independently. The judge is already close to deterministic
  (fixed seed, `reasoning_effort = "none"`, no temperature), so repeating it
  would measure almost nothing; judge variance belongs to the separate judge
  reliability check.
- **`N = 1` is the default**, and is identical to a single-pass run. `N` is a
  per-run parameter recorded in run metadata, not a frozen part of the protocol.
- **Every pass is retained in full** — its own answers, judgments, raw archive,
  and aggregate — so any pass can be inspected or re-judged later.
- **Two different spreads are reported and never merged.** The per-question
  bootstrap CI below describes uncertainty *within* one pass, over questions.
  The across-pass spread describes run-to-run sampling variance, and is
  reported as the mean plus the range and standard deviation of the per-pass
  scores. A multi-pass headline score must state both.

## Aggregation

The headline score is the arithmetic mean of all 160 turn scores. Also report
turn-1, turn-2, and eight category means. Keep the raw judge JSON and calculate
bootstrap 95% confidence intervals over questions, resampling both turns of a
question together.

## Language identification

Report the share of answers written in Polish as a **separate descriptive
statistic, never as a hidden score multiplier**. Answer language already affects
the score through the judge's `polish` dimension (0–1 per turn); this statistic
is for describing a model's behaviour, not for scoring it.

Identification uses **OpenLID v3** (`HPLT/OpenLID-v3`), a fastText classifier
over roughly 200 languages, rather than any hand-written heuristic. Each scored
answer falls into exactly one bucket, and all buckets are reported:

| Bucket | Meaning |
|---|---|
| `polish` | `pol_Latn` at confidence ≥ 0.5 |
| `other` | another language at confidence ≥ 0.5; the labels are listed |
| `no_content` | `zxx_Zxxx` — tables, code, or bare numbers, not a language failure |
| `empty` | the model produced no answer; a generation failure, not a language one |
| `undetermined` | the classifier's best label is below the 0.5 confidence threshold |

Everything stays in the denominator, so the Polish share is never flattered by
quietly dropping the cases the detector could not resolve.
