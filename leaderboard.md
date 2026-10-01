# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | API | myślenie | przeb. | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek-V4.1-Flash (:nitro) | chat | low | 3 | **9,29** | 9,22–9,34 | 0 | 91% | 8,65 | 9,50 | 9,27 | 9,93 | 9,82 | 9,23 | 8,80 | 9,15 |
| GLM-5.3-Flash (OpenRouter) | chat | tak | 3 | **8,71** | 8,58–8,79 | 1 | 96% | 7,68 | 8,32 | 8,85 | 10,00 | 9,49 | 8,98 | 8,22 | 8,19 |
| Muse-Glimmer-30B | chat | low | 3 | **8,18** | 8,11–8,29 | 0 | 91% | 7,13 | 7,87 | 8,50 | 9,65 | 8,77 | 8,88 | 7,20 | 7,47 |
| Ling-3.0-Flash | chat | tak* | 3 | **7,73** | 7,70–7,78 | 0 | 91% | 5,82 | 6,57 | 8,62 | 9,70 | 8,68 | 9,18 | 7,20 | 6,05 |
| gpt-oss-120b | chat | high | 3 | **7,64** | 7,54–7,75 | 0 | 89% | 7,02 | 6,42 | 7,60 | 9,90 | 8,47 | 8,68 | 6,30 | 6,75 |
| MiMo-v2.5 | chat | low | 3 | **7,56** | 7,48–7,71 | 2 | 88% | 5,79 | 6,59 | 8,48 | 9,89 | 8,14 | 8,85 | 6,67 | 6,07 |
| Bielik-11B-v3-Instruct | chat | brak | 3 | **7,53** | 7,30–7,74 | 0 | 94% | 6,83 | 7,45 | 7,35 | 9,06 | 6,55 | 8,25 | 7,00 | 7,78 |
| Nemotron-3.5-Lightning | chat | low | 3 | **7,36** | 7,27–7,42 | 0 | 62% | 5,77 | 6,10 | 7,62 | 9,72 | 8,93 | 8,37 | 6,23 | 6,13 |
| Bielik-PL-11B-v3.0-Instruct | chat | brak | 3 | **7,27** | 7,15–7,46 | 0 | 94% | 6,78 | 6,88 | 7,76 | 8,79 | 6,27 | 7,98 | 6,87 | 6,92 |
| gpt-oss-20b | chat | high | 3 | **7,26** | 7,21–7,33 | 1 | 89% | 6,20 | 5,32 | 8,00 | 9,86 | 9,05 | 8,47 | 5,75 | 5,50 |
| Bielik-PL-Minitron-7B-v3.0-Instruct | chat | brak | 3 | **6,41** | 6,29–6,58 | 0 | 94% | 6,25 | 5,99 | 5,77 | 8,66 | 5,00 | 7,07 | 6,10 | 6,50 |
| Bielik-4.5B-v3-Instruct | chat | brak | 3 | **5,69** | 5,60–5,86 | 0 | 97% | 4,77 | 5,73 | 5,35 | 8,54 | 4,87 | 5,85 | 5,03 | 5,55 |
| Bielik-1.5B-v3-Instruct | chat | brak | 3 | **3,83** | 3,72–3,96 | 0 | 93% | 3,95 | 4,00 | 2,77 | 6,02 | 2,87 | 4,15 | 3,38 | 3,65 |
| Qra-13B-chat | chat | brak | 3 | **3,30** | 3,12–3,40 | 0 | 90% | 3,90 | 4,03 | 3,87 | 2,05 | 1,53 | 3,32 | 3,57 | 4,12 |
| poziomka-instruct-2026-09-30-7 (16k/640k, t0,6 min_p) | chat | nie | 3 | **1,66** | 1,56–1,78 | 0 | 94% | 2,85 | 2,72 | 1,43 | 0,89 | 0,25 | 0,97 | 1,72 | 2,38 |
| poziomka-instruct-2026-09-30-1 (8k/84k, t0,8) | chat | nie | 3 | **1,65** | 1,52–1,85 | 0 | 95% | 2,52 | 2,66 | 1,72 | 1,43 | 0,32 | 0,83 | 1,38 | 2,42 |
| poziomka-instruct-2026-09-30-5 (8k/84k, t0,8) | chat | nie | 3 | **1,64** | 1,58–1,70 | 0 | 94% | 2,72 | 2,24 | 1,53 | 1,13 | 0,45 | 0,67 | 1,83 | 2,55 |
| poziomka-instruct-2026-09-30-6 (8k/84k) | chat | nie | 3 | **1,61** | 1,44–1,83 | 0 | 95% | 2,00 | 2,58 | 1,78 | 1,42 | 0,80 | 1,13 | 1,55 | 1,63 |
| poziomka-instruct-2026-09-30-4 (8k/84k, t0,8) | chat | nie | 3 | **1,58** | 1,44–1,70 | 0 | 92% | 2,55 | 2,57 | 1,60 | 0,91 | 0,32 | 0,77 | 1,50 | 2,38 |
| poziomka-instruct-2026-09-30-6 (8k/84k, t0,8) | chat | nie | 3 | **1,58** | 1,49–1,62 | 0 | 96% | 2,43 | 2,45 | 1,65 | 0,98 | 0,58 | 0,97 | 1,50 | 2,02 |
| poziomka-instruct-2026-09-30-7 (8k/84k) | chat | nie | 3 | **1,57** | 1,28–1,88 | 0 | 93% | 2,33 | 2,23 | 1,77 | 1,35 | 0,38 | 0,97 | 1,48 | 2,05 |
| poziomka-instruct-2026-09-30-5 (8k/84k) | chat | nie | 3 | **1,54** | 1,49–1,61 | 0 | 94% | 2,15 | 2,27 | 1,25 | 1,46 | 0,58 | 1,23 | 1,40 | 1,95 |
| poziomka-instruct-2026-09-30-7 (8k/84k, t0,8) | chat | nie | 3 | **1,54** | 1,49–1,62 | 0 | 94% | 2,55 | 2,37 | 1,45 | 0,88 | 0,38 | 0,77 | 1,58 | 2,35 |
| poziomka-instruct-2026-09-30-1 (8k/84k) | chat | nie | 3 | **1,51** | 1,41–1,67 | 0 | 92% | 2,22 | 2,38 | 1,52 | 1,50 | 0,47 | 0,93 | 1,53 | 1,52 |
| poziomka-instruct-2026-09-30-3 (8k/84k) | chat | nie | 3 | **1,50** | 1,41–1,60 | 0 | 93% | 2,50 | 2,30 | 1,43 | 1,65 | 0,17 | 0,85 | 1,43 | 1,68 |
| poziomka sft 2026-09-24/iter_0000100 (8k/84k) | chat | nie | 3 | **1,48** | 1,39–1,60 | 0 | 94% | 2,02 | 2,07 | 1,17 | 1,58 | 0,30 | 0,98 | 1,92 | 1,82 |
| poziomka-instruct-2026-09-30-1 (16k/640k, t0,8) | chat | nie | 3 | **1,47** | 1,42–1,52 | 0 | 95% | 2,62 | 2,47 | 1,18 | 0,84 | 0,22 | 0,87 | 1,34 | 2,25 |
| poziomka sft 2026-09-24/iter_0000498 (8k/84k) | chat | nie | 3 | **1,45** | 1,40–1,49 | 0 | 95% | 2,55 | 2,33 | 1,53 | 1,08 | 0,38 | 0,51 | 1,27 | 1,91 |
| poziomka sft 2026-09-24/iter_0000498 (8k/84k, t0,8) | chat | nie | 3 | **1,44** | 1,36–1,54 | 0 | 94% | 2,55 | 2,25 | 1,10 | 1,49 | 0,28 | 0,55 | 1,22 | 2,10 |
| poziomka sft 2026-09-24/iter_0000498 | chat | nie | 3 | **1,42** | 1,30–1,50 | 0 | 95% | 2,32 | 2,33 | 1,13 | 1,24 | 0,22 | 0,77 | 1,73 | 1,62 |
| poziomka-instruct-2026-09-30-7 (8k/84k) | chat | tak | 3 | **1,41** | 1,26–1,54 | 42 | 84% | 2,43 | 2,25 | 1,00 | 1,35 | 0,30 | 1,13 | 1,37 | 1,42 |
| poziomka sft 2026-09-14/iter_0001718 | chat | nie | 3 | **1,40** | 1,31–1,51 | 0 | 93% | 2,28 | 2,09 | 1,75 | 0,95 | 0,05 | 0,77 | 1,25 | 2,12 |
| poziomka sft 2026-09-24/iter_0000100 | chat | nie | 3 | **1,40** | 1,27–1,49 | 0 | 94% | 2,05 | 1,84 | 1,72 | 1,00 | 0,43 | 0,92 | 1,38 | 1,85 |
| poziomka sft 2026-09-14/iter_0001200 | chat | nie | 3 | **1,40** | 1,30–1,46 | 0 | 90% | 2,50 | 2,01 | 1,62 | 1,25 | 0,17 | 0,57 | 0,83 | 2,27 |
| poziomka-instruct-2026-09-30-1 (16k/640k) | chat | nie | 3 | **1,37** | 1,36–1,41 | 0 | 95% | 2,27 | 2,20 | 1,50 | 1,31 | 0,37 | 0,85 | 1,22 | 1,28 |
| poziomka-instruct-2026-09-30-4 (8k/84k) | chat | nie | 3 | **1,37** | 1,27–1,52 | 0 | 94% | 2,00 | 2,43 | 1,42 | 1,15 | 0,30 | 0,98 | 1,13 | 1,50 |
| poziomka-instruct-2026-09-30-3 (8k/84k, t0,8) | chat | nie | 3 | **1,30** | 1,28–1,32 | 0 | 94% | 2,38 | 2,10 | 1,05 | 0,77 | 0,32 | 0,70 | 1,38 | 1,65 |
| poziomka-instruct-2026-09-30-5 (8k/84k) | chat | tak | 3 | **1,28** | 1,24–1,34 | 49 | 82% | 2,50 | 2,11 | 0,72 | 1,37 | 0,34 | 0,77 | 1,23 | 1,23 |
| poziomka sft 2026-09-24/iter_0000100 (8k/84k) | chat | tak | 3 | **1,24** | 1,11–1,44 | 51 | 83% | 2,27 | 2,35 | 0,90 | 0,87 | 0,07 | 0,95 | 0,98 | 1,53 |
| poziomka-instruct-2026-09-30-5 (8k/84k, t0,8) | chat | tak | 3 | **1,22** | 1,14–1,35 | 19 | 90% | 2,60 | 1,73 | 1,10 | 0,91 | 0,12 | 0,78 | 0,87 | 1,63 |
| poziomka-instruct-2026-09-30-1 (8k/84k) | chat | tak | 3 | **1,21** | 1,16–1,27 | 51 | 82% | 2,23 | 1,92 | 0,92 | 1,05 | 0,48 | 0,85 | 0,98 | 1,28 |
| poziomka sft 2026-09-24/iter_0000498 | chat | tak | 3 | **1,21** | 1,10–1,27 | 23 | 86% | 2,65 | 1,93 | 0,68 | 1,22 | 0,15 | 0,67 | 1,12 | 1,23 |
| poziomka-instruct-2026-09-30-6 (8k/84k) | chat | tak | 3 | **1,21** | 1,11–1,29 | 47 | 80% | 2,32 | 1,90 | 0,75 | 1,22 | 0,28 | 0,75 | 1,23 | 1,25 |
| poziomka-instruct-2026-09-30-7 (8k/84k, t0,8) | chat | tak | 3 | **1,20** | 1,11–1,28 | 30 | 88% | 2,72 | 1,80 | 1,15 | 0,85 | 0,12 | 0,65 | 0,83 | 1,47 |
| poziomka-instruct-2026-09-30-7 (16k/640k, t0,6 min_p) | chat | tak | 3 | **1,20** | 1,16–1,22 | 32 | 87% | 2,55 | 1,78 | 0,82 | 0,85 | 0,40 | 0,70 | 1,13 | 1,32 |
| poziomka-instruct-2026-09-30-6 (8k/84k, t0,8) | chat | tak | 3 | **1,18** | 1,10–1,25 | 27 | 88% | 2,63 | 1,94 | 0,55 | 1,00 | 0,15 | 0,78 | 0,75 | 1,65 |
| poziomka sft 2026-09-24/iter_0000498 (8k/84k) | chat | tak | 3 | **1,17** | 1,08–1,25 | 42 | 85% | 2,38 | 1,85 | 0,67 | 1,15 | 0,19 | 0,70 | 0,97 | 1,43 |
| poziomka sft 2026-09-14/iter_0000800 | chat | nie | 3 | **1,12** | 1,08–1,15 | 0 | 94% | 2,24 | 1,88 | 0,82 | 0,50 | 0,18 | 0,28 | 0,81 | 2,22 |
| poziomka-instruct-2026-09-30-1 (16k/640k, t0,8) | chat | tak | 3 | **1,11** | 1,03–1,15 | 39 | 88% | 2,52 | 1,85 | 0,52 | 0,84 | 0,45 | 0,48 | 0,65 | 1,52 |
| poziomka sft 2026-09-24/iter_0000100 | chat | tak | 3 | **1,10** | 0,97–1,21 | 33 | 86% | 2,02 | 1,53 | 0,82 | 1,10 | 0,42 | 0,77 | 1,05 | 1,12 |
| poziomka-instruct-2026-09-30-1 (8k/84k, t0,8) | chat | tak | 3 | **1,08** | 1,06–1,10 | 33 | 86% | 2,80 | 1,65 | 0,47 | 0,43 | 0,28 | 0,73 | 0,80 | 1,42 |
| poziomka sft 2026-09-24/iter_0000498 (8k/84k, t0,8) | chat | tak | 3 | **1,08** | 0,96–1,22 | 45 | 85% | 2,23 | 1,87 | 0,37 | 1,05 | 0,47 | 0,73 | 0,67 | 1,28 |
| poziomka sft 2026-09-24/iter_0000200 (8k/84k) | chat | nie | 3 | **1,07** | 1,02–1,12 | 0 | 93% | 2,08 | 1,35 | 1,40 | 1,22 | 0,20 | 0,65 | 0,72 | 0,97 |
| poziomka sft 2026-09-14/iter_0001718 | compl. | tak | 3 | **1,06** | 0,92–1,16 | 12 | 87% | 2,07 | 1,86 | 0,97 | 1,22 | 0,05 | 0,58 | 0,55 | 1,22 |
| poziomka-instruct-2026-09-30-1 (16k/640k) | chat | tak | 3 | **1,04** | 0,87–1,16 | 34 | 85% | 1,73 | 1,83 | 0,60 | 1,43 | 0,28 | 0,68 | 0,48 | 1,25 |
| poziomka sft 2026-09-14/iter_0000400 | chat | nie | 3 | **1,04** | 0,95–1,13 | 0 | 90% | 2,12 | 1,62 | 0,95 | 0,60 | 0,05 | 0,53 | 0,80 | 1,60 |
| poziomka-instruct-2026-09-30-3 (8k/84k, t0,8) | chat | tak | 3 | **1,01** | 1,00–1,03 | 21 | 90% | 2,18 | 1,53 | 0,90 | 0,71 | 0,13 | 0,62 | 0,82 | 1,22 |
| poziomka-instruct-2026-09-30-3 (8k/84k) | chat | tak | 3 | **1,00** | 0,87–1,09 | 55 | 81% | 1,97 | 1,50 | 0,75 | 1,11 | 0,08 | 0,53 | 0,69 | 1,42 |
| poziomka sft 2026-09-24/iter_0000200 (8k/84k, t0,8) | chat | nie | 3 | **0,98** | 0,91–1,03 | 0 | 96% | 1,63 | 1,25 | 1,12 | 1,30 | 0,18 | 0,30 | 0,89 | 1,15 |
| polanka-3.7B-exp | compl. | tak | 3 | **0,97** | 0,81–1,19 | 0 | 88% | 1,60 | 1,53 | 1,07 | 1,10 | 0,45 | 0,57 | 0,40 | 1,08 |
| poziomka-instruct-2026-09-30-4 (8k/84k, t0,8) | chat | tak | 3 | **0,97** | 0,91–1,02 | 39 | 86% | 2,27 | 1,28 | 0,40 | 1,12 | 0,08 | 0,52 | 0,62 | 1,45 |
| polanka-3.7B-exp | chat | brak | 3 | **0,95** | 0,87–1,00 | 8 | 87% | 1,50 | 1,27 | 1,02 | 1,29 | 0,47 | 0,55 | 0,37 | 1,13 |
| poziomka-instruct-2026-09-30-4 (8k/84k) | chat | tak | 3 | **0,94** | 0,89–0,99 | 70 | 79% | 2,05 | 1,73 | 0,55 | 0,80 | 0,22 | 0,63 | 0,58 | 0,93 |
| polka-1.1b-chat | chat | brak | 3 | **0,88** | 0,80–1,01 | 0 | 97% | 1,28 | 1,63 | 0,81 | 0,57 | 0,45 | 0,38 | 0,47 | 1,45 |
| poziomka sft 2026-09-24/iter_0000300 (8k/84k) | chat | nie | 3 | **0,87** | 0,83–0,89 | 0 | 91% | 1,80 | 0,85 | 1,35 | 1,22 | 0,30 | 0,42 | 0,47 | 0,53 |
| poziomka sft 2026-09-24/iter_0000300 (8k/84k) | chat | tak | 3 | **0,84** | 0,76–0,92 | 53 | 80% | 1,77 | 1,17 | 0,98 | 0,64 | 0,43 | 0,75 | 0,43 | 0,57 |
| poziomka sft 2026-09-24/iter_0000300 (8k/84k, t0,8) | chat | nie | 3 | **0,82** | 0,76–0,87 | 0 | 95% | 1,85 | 0,90 | 1,32 | 0,58 | 0,13 | 0,33 | 0,62 | 0,82 |
| poziomka sft 2026-09-24/iter_0000200 (8k/84k) | chat | tak | 3 | **0,81** | 0,70–1,04 | 66 | 78% | 1,72 | 1,30 | 0,75 | 0,90 | 0,18 | 0,42 | 0,67 | 0,58 |
| poziomka sft 2026-09-24/iter_0000200 (8k/84k, t0,8) | chat | tak | 3 | **0,80** | 0,73–0,89 | 55 | 79% | 1,68 | 0,95 | 0,72 | 0,85 | 0,32 | 0,23 | 0,53 | 1,08 |
| poziomka sft 2026-09-21/iter_0000100 | chat | nie* | 3 | **0,79** | 0,75–0,85 | 48 | 82% | 1,43 | 1,31 | 0,60 | 0,61 | 0,30 | 0,77 | 0,73 | 0,55 |
| poziomka sft 2026-09-24/iter_0000300 (8k/84k, t0,8) | chat | tak | 3 | **0,70** | 0,66–0,73 | 55 | 80% | 1,55 | 0,76 | 0,83 | 0,71 | 0,25 | 0,42 | 0,30 | 0,78 |
| poziomka sft 2026-09-14/iter_0000800 | chat | tak | 3 | **0,68** | 0,62–0,71 | 42 | 70% | 1,17 | 0,51 | 0,37 | 0,99 | 0,23 | 0,33 | 0,38 | 1,42 |
| poziomka sft 2026-09-09/iter_0000400 | compl. | mixed 53% | 3 | **0,66** | 0,62–0,72 | 0 | 94% | 1,35 | 0,85 | 0,68 | 0,63 | 0,15 | 0,22 | 0,53 | 0,92 |
| poziomka sft 2026-09-09/iter_0000400 | compl. | tak | 3 | **0,66** | 0,61–0,71 | 22 | 80% | 1,33 | 0,98 | 0,85 | 0,46 | 0,07 | 0,27 | 0,28 | 1,03 |
| poziomka sft 2026-09-14/iter_0001718 | chat | tak | 3 | **0,59** | 0,55–0,63 | 45 | 69% | 1,08 | 0,41 | 0,37 | 0,79 | 0,02 | 0,45 | 0,53 | 1,08 |
| poziomka sft 2026-09-14/iter_0000400 | chat | tak | 3 | **0,50** | 0,45–0,57 | 50 | 65% | 1,07 | 0,38 | 0,33 | 0,51 | 0,40 | 0,40 | 0,10 | 0,83 |
| poziomka sft 2026-09-14/iter_0001200 | chat | tak | 3 | **0,41** | 0,29–0,47 | 62 | 57% | 0,75 | 0,52 | 0,17 | 0,48 | 0,02 | 0,25 | 0,30 | 0,77 |
| APT3-1B-Instruct-v1 | compl. | brak | 3 | **0,38** | 0,34–0,44 | 0 | 94% | 0,53 | 0,53 | 0,45 | 0,48 | 0,17 | 0,30 | 0,13 | 0,47 |
| poziomka sft 2026-09-21/iter_0000100 | chat | tak | 3 | **0,37** | 0,29–0,41 | 245 | 43% | 0,55 | 0,81 | 0,48 | 0,45 | 0,07 | 0,15 | 0,19 | 0,25 |
| poziomka sft 2026-09-21/iter_0000535 | chat | nie | 3 | **0,21** | 0,20–0,21 | 21 | 59% | 0,48 | 0,29 | 0,29 | 0,52 | 0,00 | 0,00 | 0,02 | 0,07 |
| poziomka sft 2026-09-21/iter_0000535 | chat | tak | 3 | **0,09** | 0,04–0,11 | 335 | 17% | 0,03 | 0,08 | 0,28 | 0,08 | 0,22 | 0,00 | 0,00 | 0,00 |

Kolumny kategorii: piśmiennictwo, odgrywanie ról, wnioskowanie, matematyka,
kodowanie, ekstrakcja, nauki ścisłe, humanistyka. „Puste" to tury, w których
model nie wygenerował odpowiedzi (na 160). „Pol." to odsetek odpowiedzi
rozpoznanych jako polskie — statystyka opisowa, nie składnik wyniku. „Rozrzut"
to zakres wyników z kolejnych przebiegów. API: `chat` to `/chat/completions`,
`compl.` to `/completions` z szablonem renderowanym lokalnie. „Myślenie: brak"
oznacza, że model nie generuje rozumowania w tej konfiguracji. `tak*` przy
Lingu: model rozumuje w każdej turze (480/480), ale dostawca nie wystawia
`reasoning_effort`, więc siły rozumowania nie da się przypiąć. `nie*` przy
`2026-09-21/iter_0000100`: szablon dostał `enable_thinking = false`, ale model
i tak rozumuje w większości tur — ta wersja serii jeszcze nie respektuje
przełącznika.

**Okno kontekstu, RoPE i temperatura.** Wiersze Poziomki bez adnotacji
zmierzono w oknie 16384 z `max_tokens = 7800`. Dopisek `(8k/84k)` oznacza serwer
postawiony z oknem 8192 i RoPE 84000; tam `max_tokens = 3500`, bo tura 2 liczy
budżet podwójnie i więcej nie mieści się w oknie. Dopisek `t0,8` oznacza
`temperature = 0,8` zamiast 0,3 — reszta samplingu bez zmian. Dopisek
`(16k/640k)` przy `poziomka-instruct-2026-09-30-1` to okno 16384 i RoPE 640000
z `max_tokens = 7800`; ten model zmierzono w obu konfiguracjach, więc obie są
oznaczone jawnie. Ta sama liczba kroków treningu
w dwóch konfiguracjach serwera daje więc dwa osobne wiersze — nie są to dwa
modele.

**Dla serii `2026-09-24` okno 8192 z RoPE 84000 jest neutralne.** Cztery pomiary
na dwóch checkpointach dają +0,08 i +0,14 przy `iter_0000100`, ale +0,03 i −0,04
przy `iter_0000498` — a rozrzut między przebiegami tego samego ustawienia sięga
0,09. Pozorny przyrost przy setnej iteracji był więc szumem. Wniosek praktyczny:
model działa tak samo przy o połowę mniejszym oknie i o połowę mniejszym
budżecie tokenów, czyli da się go serwować taniej bez straty jakości. Krótszy
budżet zmniejsza za to zapętlenia (9% wobec 13% w wariancie `nie`), bo model ma
mniej miejsca na dryf w powtórzenia; w wariancie `tak` kosztuje jednak więcej
pustych tur (42 wobec 23), bo ślad rozumowania częściej nie zdąża się domknąć.

**Temperatura działa przeciwnie w obu wariantach.** Wartość 0,3 dobrano na
wczesnym checkpoincie, gdzie przy wyższej temperaturze model tracił spójność;
po pełnej epoce na wyczyszczonym korpusie ten kompromis przestał być potrzebny —
ale tylko bez rozumowania:

| `iter_0000498` (8k/84k) | t0,3 | t0,8 |
|---|---|---|
| `nie` | 1,45 | 1,44 |
| `tak` | 1,17 | 1,08 |

Bez rozumowania 0,8 jest darmowe: wynik ten sam, a zapętlenia spadają z 9% do
2% tur, bez kosztu w polszczyźnie (94% wobec 95%) ani w pustych turach (0
w obu). Z rozumowaniem zapętlenia też spadają (11% → 4%), lecz wynik traci 0,09,
i to w kategoriach, w których rozumowanie ma pomagać: wnioskowanie 0,67 → 0,37,
nauki ścisłe 0,97 → 0,67. Liczba pustych tur prawie się nie zmienia (42 → 45),
więc nie chodzi o to, że ślad przestaje się domykać — wyższa temperatura
rozprasza samo rozumowanie. Zalecenie dla tej serii: 0,8 dla `nie`, 0,3 dla
`tak`. W obu przypadkach różnice mieszczą się w rozrzucie między przebiegami,
więc mocniejszy jest argument z zapętleń niż z samego wyniku.

Inaczej wypada seria `2026-09-21`: `iter_0000535` przy przejściu na okno 16384
traci połowę wyniku (0,53 → 0,24), i to na krótkich promptach, gdzie długość
okna nie powinna mieć znaczenia. Skoro `2026-09-24` przenosi się między tymi
konfiguracjami bez szkody, wskazuje to na błędną konfigurację RoPE w tamtym
checkpoincie, a nie na wadę samego mechanizmu; wyniki `2026-09-21/iter_0000535`
z obu konfiguracji zostały do czasu wyjaśnienia poza tabelą.

**`poziomka-instruct-2026-09-30-1` to merge kilku checkpointów**, nie pojedynczy
krok treningu — stąd nazwa bez numeru iteracji. Jest to najwyżej oceniona
Poziomka w tabeli (1,65 wobec 1,48 poprzedniego lidera), przy zerze pustych tur
i 95% polszczyzny. Zmierzono go w obu konfiguracjach serwera i przy obu
temperaturach, osiem wierszy łącznie:

| `poziomka-instruct-2026-09-30-1` | 8k/84k | 16k/640k |
|---|---|---|
| `nie`, t0,3 | 1,51 | 1,37 |
| `nie`, t0,8 | **1,65** | 1,47 |
| `tak`, t0,3 | 1,21 | 1,04 |
| `tak`, t0,8 | 1,08 | 1,11 |

**Dla tego modelu okno 8192 z RoPE 84000 jest wyraźnie lepsze** — o 0,14 do 0,18
w trzech z czterech kombinacji, a przy `nie`/t0,8 przedziały rozrzutu nawet się
nie dotykają (1,52–1,85 wobec 1,42–1,52). Reakcja na konfigurację RoPE okazuje
się więc zależna od modelu: seria `2026-09-24` jest na tę zmianę obojętna,
`2026-09-21/iter_0000535` traci połowę wyniku, a merge traci spójnie, ale
umiarkowanie. Każdy model trzeba zmierzyć osobno.

**Temperatury nie da się ustalić raz dla wszystkich Poziomek** — zależy od tego,
w czym dany model jest mocny. Trzy merge'y na oknie 8192, wariant bez
rozumowania:

| merge | t0,3 | t0,8 | zmiana | matematyka przy t0,3 |
|---|---|---|---|---|
| `-1` | 1,51 | **1,65** | +0,14 | 1,50 |
| `-3` | **1,50** | 1,30 | −0,20 | 1,65 |
| `-4` | 1,37 | **1,58** | +0,21 | 1,15 |
| `-5` | 1,54 | **1,64** | +0,10 | 1,46 |
| `-6` | **1,61** | 1,58 | −0,03 | 1,42 |
| `-7` | **1,57** | 1,54 | −0,03 | 1,35 |

Wyższa temperatura pomaga modelom mocnym w tekstach otwartych, a szkodzi tym
mocnym w matematyce: `-3` ma najlepszą matematykę wśród Poziomek (1,65)
i traci 0,20, natomiast `-1` i `-4` mają ją słabszą i zyskują po ok. 0,2. Wzorzec
widać też w kategoriach — przy t0,8 `-4` rośnie w humanistyce (1,50 → 2,38)
i odgrywaniu ról (2,43 → 2,57), a matematyka spada (1,15 → 0,91).

Zapętlenia spadają przy wyższej temperaturze zawsze, we wszystkich merge'ach
(14% → 6% u `-4`, 11% → 3% u `-3`), ale u `-3` ta poprawa nie kompensuje strat
w treści. Wielkość zysku idzie w parze z tym, ile jest do ugaszenia: `-4` miał
14% zapętleń przy t0,3 i zyskuje 0,21, a `-5` tylko 10% i zyskuje 0,10.

**Udział wczesnych checkpointów w merge'u działa przeciwnie w obu wariantach.**
`-5` i `-7` składają się z tych samych dziewięciu checkpointów i różnią się
wyłącznie wagą grupy run2 (korpus v11, okno 8192): 25,5% wobec 9,6%.

| | `-5` (run2 25,5%) | `-7` (run2 9,6%) |
|---|---|---|
| `nie`, t0,8 | **1,64** | 1,54 |
| `tak`, t0,3 | 1,28 | **1,41** |

Odchudzenie run2 kosztuje 0,10 bez rozumowania, a daje 0,13 z rozumowaniem.
Wczesne checkpointy wnoszą więc coś, co pomaga w trybie bezpośrednim,
a przeszkadza przy rozumowaniu. `-7` ma najlepszy wariant `tak` w całej tabeli
(1,41), a także najwyższą ekstrakcję (1,13) i wnioskowanie (1,00) w tym
wariancie.

**Seria `2026-09-24` ma dołek w środku treningu, nie plateau.** Przez długi czas
mieliśmy z run4 tylko `iter_0000100` i `iter_0000498` — dwa punkty oddalone
o cztery miliardy tokenów, między którymi krzywa wyglądała na płaską. Pomiar
`iter_0000200` pokazuje co innego:

| checkpoint | tokeny SFT | `nie` | `tak` |
|---|---|---|---|
| `iter_0000100` | 3,90 mld | 1,48 | 1,24 |
| `iter_0000200` | 4,89 mld | 1,07 | 0,81 |
| `iter_0000300` | 5,88 mld | **0,87** | **0,84** |
| `iter_0000498` | 7,85 mld | 1,45 | 1,17 |

Zagłębienie jest szerokie i pogłębia się aż do trzysetki: bez rozumowania
spadek sięga 0,61, czyli ponad 40% wyniku, i odbudowuje się dopiero na ostatnim
odcinku. Wniosek: **nie wolno interpolować między odległymi checkpointami** —
płaski odcinek na wykresie może ukrywać załamanie.

W kategoriach widać, co się psuje. Między `iter_0000100` a `iter_0000300` bez
rozumowania nauki ścisłe spadają z 1,92 do 0,47, humanistyka z 1,82 do 0,53,
ekstrakcja z 0,98 do 0,42, a piśmiennictwo trzyma się najlepiej (2,02 → 1,80).
Model traci więc wiedzę i precyzję, zachowując płynność. Przy `iter_0000300`
oba warianty prawie się zrównują (0,87 wobec 0,84), bo spada głównie ten bez
rozumowania.

Uwagi przy czytaniu: wiersz `iter_0000200`/`tak` ma szeroki rozrzut
(0,70–1,04) i 66 pustych tur na 480 (14%). Warianty `tak` dla `iter_0000300`
mierzono dwukrotnie — pierwszy pomiar unieważniła awaria GPU, która dała
160/160 nieudanych zapytań w kilku przebiegach; w tabeli jest powtórka
z zerem błędów.

**Sampler trzeba dobierać pod konfigurację RoPE, bo kierunek się odwraca.**
Wiersz `-7 (16k/640k, t0,6 min_p)` to `temperature = 0,6`, `top_p = 0,9`,
`min_p = 0,05`, `frequency_penalty = 0,15`. Na RoPE 84000 najlepsza dla
rozumowania była temperatura 0,9 (1 pusta tura na 48 prób), a 0,3 najgorsza
(5/48); na RoPE 640000 jest odwrotnie — przy 0,9 wychodzi 4–9/48, a najlepiej
wypada 0,5–0,6. Odrzucone na tej konfiguracji: `top_k` 20/40 i
`repetition_penalty` z zakresem dawały więcej pustych i urwanych tur, samo
`min_p` bez obniżenia temperatury schodziło tylko do 6/48.

Ten wiersz pokazuje też, że **czystsza generacja nie znaczy lepszy wynik**.
Wobec `-7 (8k/84k)` puste tury spadły z 42 do 32, a zapętlone z 11% do 1%, ale
wariant z rozumowaniem stracił 0,21 (1,41 → 1,20) — na wnioskowaniu, ekstrakcji
i naukach ścisłych. Bez rozumowania ta sama zmiana dała najwyższy wynik Poziomki
w tabeli (1,66). RoPE 640000 psuje więc samo rozumowanie, a sampler sprząta
wyłącznie objawy. Budżet nie jest tu winny: zero urwanych zapytań na 480 tur,
a w sondzie `max_tokens` 12000 i brak limitu dawały tyle samo pustych tur co
7800.

**Ostrożnie z wierszami `nie`/t0,3 u `-6` i `-7`.** Mają rozrzut 1,44–1,83
i 1,28–1,88 (odchylenie 0,20 i 0,30) — najszersze w tabeli. Przy takich
przedziałach różnice rzędu 0,05 między merge'ami nic nie znaczą i nie należy
na nich budować rankingu.

**`-5` jest najrówniejszym merge'em.** Wygrywa w trzech z czterech kombinacji,
a w czwartej remisuje z `-1` (1,64 wobec 1,65, przedziały 1,58–1,70 i 1,52–1,85
zachodzą). Ma najlepszy wynik z rozumowaniem wśród wszystkich Poziomek (1,28)
oraz najlepsze kodowanie (0,58) i ekstrakcję (1,23). Jest też najstabilniejszy:
rozrzut 0,06 w trzech kombinacjach, wobec 0,13–0,18 u `-1` i `-4`. Z rozumowaniem wyższa temperatura psuje kategorie analityczne
u wszystkich trzech — u `-1` matematyka 1,05 → 0,43 i wnioskowanie 0,92 → 0,47 —
choć zmniejsza puste tury (u `-4` z 70 do 39).

Serie Poziomki nazwane są datą publikacji repozytorium:
`sft 2026-09-14` to [`cpral/poziomka_sft_2026_09_14_hf`](https://huggingface.co/cpral/poziomka_sft_2026_09_14_hf),
a `sft 2026-09-09` to `cpral/poziomka_sft_2026_09_09_hf` (lokalnie katalogi
`poziomka_sft_run2_v11_8192_hf` i `poziomka_sft_run2_09_09_hf`), a
`sft 2026-09-21` to `cpral/poziomka_sft_2026_09_21_hf` (lokalnie
`poziomka_sft_run3_v11_16384_hf`), a `sft 2026-09-24` to
`cpral/poziomka_sft_2026_09_24_hf` (lokalnie `poziomka_sft_run4_v12_16384_hf`).
Obie ostatnie serie mają okno kontekstu 16384 zamiast 8192.

**Wiersze `myślenie: tak` Poziomki poza `2026-09-24` są zaniżone.** Mierzono je
kodem, który przy otwartym bloku `<think>` kasował odpowiedzi modeli
odpowiadających bez rozumowania: pusty `reasoning_content` z serwera brano za
brak parsera i całą treść traktowano jako niezamknięty ślad. Po poprawce liczba
pustych tur w `2026-09-24` spadła z 132 do 33, a wynik wzrósł z 0,73 do 1,10.
Wiersze `2026-09-14`, `2026-09-09` oraz `2026-09-21/iter_0000535` czekają na
ponowny pomiar; do tego czasu traktuj je jako dolne oszacowanie. Oba wiersze
`2026-09-21/iter_0000100` i `2026-09-24` zmierzono już poprawionym kodem. Wiersze `nie`/`brak` oraz
modele z OpenRoutera są nietknięte, bo tam prompt nie zostawia otwartego bloku.

Sampling protokolarny to `temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`; sędzia wszędzie ten sam (`openai/gpt-5.6-luna`,
`reasoning_effort = none`, `seed = 42`). Odstępstwa, dopuszczone przez protokół:

- **Muse-Glimmer**: sampling zalecany przez kartę modelu (1,0 / 0,95 / top_k 64,
  bez repetition penalty).
- **GLM 5.3 Flash**: sampling zalecany przez kartę (1,0 / 0,95, bez top_k
  i bez repetition penalty).
- **MiMo v2.5**: sampling protokolarny bez repetition penalty,
  `reasoning_effort = low`.
- **Ling 3.0 Flash**: sampling protokolarny bez repetition penalty; siły
  rozumowania nie da się ustawić, bo dostawca nie obsługuje `reasoning_effort`.
- **DeepSeek V4.1 Flash i Nemotron 3.5 Lightning**: sampling protokolarny bez
  repetition penalty, `reasoning_effort = low`. Nemotron nie obsługuje `top_k`
  ani repetition penalty, więc idzie tylko na `temperature` i `top_p`. DeepSeek
  używa wariantu `:nitro`, który sortuje endpointy po przepustowości.
- **gpt-oss 20B i 120B**: sampling protokolarny, ale bez repetition penalty —
  kara za powtórzenia jest nie na miejscu przy modelu, który powtarza wątki
  w śladzie rozumowania.
- **Poziomka `sft 2026-09-24` i `sft 2026-09-21/iter_0000100`**:
  `temperature = 0,3`, `top_p = 0,9`,
  `frequency_penalty = 0,05`, bez `top_k` i bez repetition penalty. Checkpoint
  zapętla się przy samplingu protokolarnym — na 16 próbach trzy tury urywały
  się na limicie tokenów, a jedna linia powtarzała się 223 razy.
  `repetition_penalty = 1,10` też gasi pętle, ale wycina konkrety (zamiast
  Giżycka i Węgorzewa zostają „wędrówki i szlaki"), bo karze jednakowo
  wszystko, co już padło. `frequency_penalty` skaluje karę liczbą wystąpień
  tokenu; wartość 0,05 wybrana pomiarem na 24 pytaniach × 2 ziarna, przy
  którym żadna tura się nie urwała (0/48).
- **`max_tokens`** musi zmieścić się w oknie kontekstu, liczonym podwójnie ze
  względu na turę 2: 3500 przy oknie 32768 i większym, 1600 dla Qry i Polki
  (okno 4096), 600 dla APT3 (okno 2048). U modeli rozumujących ślad wchodzi do
  tego samego budżetu co odpowiedź, stąd 40000 dla GLM-a i obu gpt-oss.

## Gromada modeli rozumujących

Cztery modele mieszczą się w 7,36–7,73: Nemotron 3.5 Lightning, MiMo v2.5,
gpt-oss-120b i Ling 3.0 Flash. Dzielące je różnice są rzędu rozrzutu między
przebiegami tego samego modelu, a profile mają niemal identyczne — matematyka
9,7–9,9, piśmiennictwo 5,8–7,0, czyli rozstrzał około czterech punktów między
najlepszą a najgorszą kategorią.

Od gromady odstają dwa modele: DeepSeek V4.1 Flash (9,29), jedyny bez słabszej
strony językowej, i GLM 5.3 Flash (8,71). Czoła tabeli nie wyznacza więc ani
skala, ani sama obecność rozumowania — rozumują wszystkie cztery modele
z gromady.

