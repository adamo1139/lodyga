# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | API | myślenie | przeb. | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash (:nitro) | chat | low | 3 | **9,29** | 9,22–9,34 | 0 | 91% | 8,65 | 9,50 | 9,27 | 9,93 | 9,82 | 9,23 | 8,80 | 9,15 |
| GLM-5.3-Flash (OpenRouter) | chat | tak | 3 | **8,71** | 8,56–8,79 | 0 | 96% | 7,65 | 8,35 | 8,88 | 10,00 | 9,50 | 9,08 | 8,10 | 8,09 |
| Muse-Glimmer-30B | chat | low | 3 | **8,18** | 8,11–8,29 | 0 | 91% | 7,13 | 7,87 | 8,50 | 9,65 | 8,77 | 8,88 | 7,20 | 7,47 |
| gpt-oss-120b | chat | high | 3 | **7,64** | 7,54–7,75 | 0 | 89% | 7,02 | 6,42 | 7,60 | 9,90 | 8,47 | 8,68 | 6,30 | 6,75 |
| Bielik-11B-v3-Instruct | chat | brak | 3 | **7,53** | 7,30–7,74 | 0 | 94% | 6,83 | 7,45 | 7,35 | 9,06 | 6,55 | 8,25 | 7,00 | 7,78 |
| Bielik-PL-11B-v3.0-Instruct | chat | brak | 3 | **7,27** | 7,15–7,46 | 0 | 94% | 6,78 | 6,88 | 7,76 | 8,79 | 6,27 | 7,98 | 6,87 | 6,92 |
| gpt-oss-20b | chat | high | 3 | **7,26** | 7,21–7,33 | 1 | 89% | 6,20 | 5,32 | 8,00 | 9,86 | 9,05 | 8,47 | 5,75 | 5,50 |
| Bielik-PL-Minitron-7B-v3.0-Instruct | chat | brak | 3 | **6,41** | 6,29–6,58 | 0 | 94% | 6,25 | 5,99 | 5,77 | 8,66 | 5,00 | 7,07 | 6,10 | 6,50 |
| Bielik-4.5B-v3-Instruct | chat | brak | 3 | **5,69** | 5,60–5,86 | 0 | 97% | 4,77 | 5,73 | 5,35 | 8,54 | 4,87 | 5,85 | 5,03 | 5,55 |
| Bielik-1.5B-v3-Instruct | chat | brak | 3 | **3,83** | 3,72–3,96 | 0 | 93% | 3,95 | 4,00 | 2,77 | 6,02 | 2,87 | 4,15 | 3,38 | 3,65 |
| Qra-13B-chat | chat | brak | 3 | **3,30** | 3,12–3,40 | 0 | 90% | 3,90 | 4,03 | 3,87 | 2,05 | 1,53 | 3,32 | 3,57 | 4,12 |
| poziomka sft 2026-09-14/iter_0001718 | chat | nie | 3 | **1,40** | 1,31–1,51 | 0 | 93% | 2,28 | 2,09 | 1,75 | 0,95 | 0,05 | 0,77 | 1,25 | 2,12 |
| poziomka sft 2026-09-14/iter_0001200 | chat | nie | 3 | **1,40** | 1,30–1,46 | 0 | 90% | 2,50 | 2,01 | 1,62 | 1,25 | 0,17 | 0,57 | 0,83 | 2,27 |
| poziomka sft 2026-09-14/iter_0000800 | chat | nie | 3 | **1,12** | 1,08–1,15 | 0 | 94% | 2,24 | 1,88 | 0,82 | 0,50 | 0,18 | 0,28 | 0,81 | 2,22 |
| poziomka sft 2026-09-14/iter_0001718 | compl. | tak | 3 | **1,06** | 0,92–1,16 | 12 | 87% | 2,07 | 1,86 | 0,97 | 1,22 | 0,05 | 0,58 | 0,55 | 1,22 |
| poziomka sft 2026-09-14/iter_0000400 | chat | nie | 3 | **1,04** | 0,95–1,13 | 0 | 90% | 2,12 | 1,62 | 0,95 | 0,60 | 0,05 | 0,53 | 0,80 | 1,60 |
| polanka-3.7B-exp | compl. | tak | 3 | **0,97** | 0,81–1,19 | 0 | 88% | 1,60 | 1,53 | 1,07 | 1,10 | 0,45 | 0,57 | 0,40 | 1,08 |
| polanka-3.7B-exp | chat | brak | 3 | **0,95** | 0,87–1,00 | 8 | 87% | 1,50 | 1,27 | 1,02 | 1,29 | 0,47 | 0,55 | 0,37 | 1,13 |
| polka-1.1b-chat | chat | brak | 3 | **0,93** | 0,83–1,01 | 0 | 97% | 1,30 | 1,75 | 0,81 | 0,65 | 0,45 | 0,43 | 0,53 | 1,48 |
| poziomka sft 2026-09-14/iter_0000800 | chat | tak | 3 | **0,68** | 0,62–0,71 | 42 | 70% | 1,17 | 0,51 | 0,37 | 0,99 | 0,23 | 0,33 | 0,38 | 1,42 |
| poziomka sft 2026-09-09/iter_0000400 | compl. | mixed 53% | 3 | **0,66** | 0,62–0,72 | 0 | 94% | 1,35 | 0,85 | 0,68 | 0,63 | 0,15 | 0,22 | 0,53 | 0,92 |
| poziomka sft 2026-09-09/iter_0000400 | compl. | tak | 3 | **0,66** | 0,61–0,71 | 22 | 80% | 1,33 | 0,98 | 0,85 | 0,46 | 0,07 | 0,27 | 0,28 | 1,03 |
| poziomka sft 2026-09-14/iter_0001718 | chat | tak | 3 | **0,59** | 0,55–0,63 | 45 | 69% | 1,08 | 0,41 | 0,37 | 0,79 | 0,02 | 0,45 | 0,53 | 1,08 |
| poziomka sft 2026-09-14/iter_0000400 | chat | tak | 3 | **0,50** | 0,45–0,57 | 50 | 65% | 1,07 | 0,38 | 0,33 | 0,51 | 0,40 | 0,40 | 0,10 | 0,83 |
| poziomka sft 2026-09-14/iter_0001200 | chat | tak | 3 | **0,41** | 0,29–0,47 | 62 | 57% | 0,75 | 0,52 | 0,17 | 0,48 | 0,02 | 0,25 | 0,30 | 0,77 |
| APT3-1B-Instruct-v1 | compl. | brak | 3 | **0,38** | 0,34–0,44 | 0 | 94% | 0,53 | 0,53 | 0,45 | 0,48 | 0,17 | 0,30 | 0,13 | 0,47 |

Kolumny kategorii: piśmiennictwo, odgrywanie ról, wnioskowanie, matematyka,
kodowanie, ekstrakcja, nauki ścisłe, humanistyka. „Puste" to tury, w których
model nie wygenerował odpowiedzi (na 160). „Pol." to odsetek odpowiedzi
rozpoznanych jako polskie — statystyka opisowa, nie składnik wyniku. „Rozrzut"
to zakres wyników z kolejnych przebiegów. API: `chat` to `/chat/completions`,
`compl.` to `/completions` z szablonem renderowanym lokalnie. „Myślenie: brak"
oznacza, że model nie generuje rozumowania w tej konfiguracji.

Serie Poziomki nazwane są datą publikacji repozytorium:
`sft 2026-09-14` to [`cpral/poziomka_sft_2026_09_14_hf`](https://huggingface.co/cpral/poziomka_sft_2026_09_14_hf),
a `sft 2026-09-09` to `cpral/poziomka_sft_2026_09_09_hf` (lokalnie katalogi
`poziomka_sft_run2_v11_8192_hf` i `poziomka_sft_run2_09_09_hf`).

Sampling protokolarny to `temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`; sędzia wszędzie ten sam (`openai/gpt-5.6-luna`,
`reasoning_effort = none`, `seed = 42`). Odstępstwa, dopuszczone przez protokół:

- **Muse-Glimmer**: sampling zalecany przez kartę modelu (1,0 / 0,95 / top_k 64,
  bez repetition penalty).
- **GLM 5.3 Flash**: sampling zalecany przez kartę (1,0 / 0,95, bez top_k
  i bez repetition penalty).
- **gpt-oss 20B i 120B**: sampling protokolarny, ale bez repetition penalty —
  kara za powtórzenia jest nie na miejscu przy modelu, który powtarza wątki
  w śladzie rozumowania.
- **`max_tokens`** musi zmieścić się w oknie kontekstu, liczonym podwójnie ze
  względu na turę 2: 3500 przy oknie 32768 i większym, 1600 dla Qry i Polki
  (okno 4096), 600 dla APT3 (okno 2048). U modeli rozumujących ślad wchodzi do
  tego samego budżetu co odpowiedź, stąd 40000 dla GLM-a i obu gpt-oss.


