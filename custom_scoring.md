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

The judge must not reward length by itself. Long reasoning is acceptable when it
supports a correct answer. Deduct for repetition, irrelevant digressions,
unusable formatting, or reasoning that obscures or contradicts the final answer.

## References

Use every non-empty `reference` supplied in `question.jsonl`, regardless of
category. A reference is evidence about the expected answer, not an instruction
to copy its wording. If a reference is incomplete, ambiguous, or appears wrong,
the judge should rely on the question and domain knowledge and mention that in
the explanation.

## Answer generation

- One answer file per model, covering all 80 questions and both turns
  (160 answers per model).
- Turn 2 is generated with the full conversation in context: question 1, the
  model's own turn-1 answer, and question 2.
- Each model is run from its own config file that specifies the model, its
  chat template, and its generation settings (sampling parameters and token
  limits). There is no protocol-wide token limit and no cross-model sampling
  requirement; the config file used is recorded in run metadata.

## Judge

- The judge is called through the **OpenRouter** chat-completions API. The
  judge model and its sampling (temperature, top-p, token limit, seed) are set
  in the judge config file. Sampling is frozen for the whole run — the same
  values apply to every judged turn — and the config file is archived with the
  results.
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

## Aggregation

The headline score is the arithmetic mean of all 160 turn scores. Also report
turn-1, turn-2, and eight category means. Keep the raw judge JSON and calculate
bootstrap 95% confidence intervals over questions, resampling both turns of a
question together. Report the percentage of answers judged to be in Polish as a
separate descriptive statistic, never as a hidden score multiplier.
