# Łodyga — scoring benchmarku rozmów wieloetapowych

Łodyga is the project-specific evaluation built from the public Polish MT-Bench
questions. It is intentionally not claimed to reproduce the SpeakLeash
leaderboard.

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
