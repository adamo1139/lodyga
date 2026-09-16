# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko modele z tej tabeli między sobą.

| model | wynik | rozrzut | przebiegi | sędzia |
|---|---|---|---|---|
| poziomka_iter_0001718 | **1,06** | 0,92–1,16 (sd 0,12) | 3 | `openai/gpt-5.6-luna` |

## poziomka_iter_0001718

Checkpoint SFT `poziomka_sft_run2_v11_8192_hf/iter_0001718`, serwowany przez
SGLang. Przebieg `20260916T001437Z__poziomka_iter_0001718__3pass`, 16 września
2026.

Wyniki kolejnych przebiegów: 1,16 · 0,92 · 1,09. Przedziały ufności w obrębie
pojedynczego przebiegu sięgają ±0,3, więc różnice tego rzędu nic nie znaczą.

| kategoria | wynik |
|---|---|
| piśmiennictwo | 2,07 |
| odgrywanie ról | 1,86 |
| matematyka | 1,22 |
| humanistyka | 1,22 |
| wnioskowanie | 0,97 |
| ekstrakcja | 0,58 |
| nauki ścisłe | 0,55 |
| kodowanie | 0,05 |

Tura 1 wypada dwa razy lepiej niż tura 2 (1,54 wobec 0,77) — model gubi wątek
przy pytaniu uzupełniającym. Od 9 do 17 tur na 160 kończy się pustą odpowiedzią:
model zapętla się w rozumowaniu i nie zamyka `</think>` przed limitem tokenów.
Sędzia najczęściej zarzuca nie tyle błędy rzeczowe, co wykonanie innego zadania
niż polecone. Po polsku jest 86,9% odpowiedzi.

Ustawienia generowania: `temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`, `max_tokens = 3500`. Sędzia: `reasoning_effort =
none`, `seed = 42`.
