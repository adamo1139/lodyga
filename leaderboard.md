# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | API | myślenie | przeb. | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bielik-11B-v3-Instruct | chat | brak | 3 | **7,53** | 7,30–7,74 | 0 | 94% | 6,83 | 7,45 | 7,35 | 9,06 | 6,55 | 8,25 | 7,00 | 7,78 |
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
| poziomka sft 2026-09-14/iter_0000800 | chat | tak | 3 | **0,68** | 0,62–0,71 | 42 | 70% | 1,17 | 0,51 | 0,37 | 0,99 | 0,23 | 0,33 | 0,38 | 1,42 |
| poziomka sft 2026-09-09/iter_0000400 | compl. | mixed 53% | 3 | **0,66** | 0,62–0,72 | 0 | 94% | 1,35 | 0,85 | 0,68 | 0,63 | 0,15 | 0,22 | 0,53 | 0,92 |
| poziomka sft 2026-09-09/iter_0000400 | compl. | tak | 3 | **0,66** | 0,61–0,71 | 22 | 80% | 1,33 | 0,98 | 0,85 | 0,46 | 0,07 | 0,27 | 0,28 | 1,03 |
| poziomka sft 2026-09-14/iter_0001718 | chat | tak | 3 | **0,59** | 0,55–0,63 | 45 | 69% | 1,08 | 0,41 | 0,37 | 0,79 | 0,02 | 0,45 | 0,53 | 1,08 |
| poziomka sft 2026-09-14/iter_0000400 | chat | tak | 3 | **0,50** | 0,45–0,57 | 50 | 65% | 1,07 | 0,38 | 0,33 | 0,51 | 0,40 | 0,40 | 0,10 | 0,83 |
| poziomka sft 2026-09-14/iter_0001200 | chat | tak | 3 | **0,41** | 0,29–0,47 | 62 | 57% | 0,75 | 0,52 | 0,17 | 0,48 | 0,02 | 0,25 | 0,30 | 0,77 |

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

Sampling identyczny wszędzie (`temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`), sędzia też (`openai/gpt-5.6-luna`,
`reasoning_effort = none`, `seed = 42`). Wyjątek: Qra ma okno 4096 tokenów,
więc `max_tokens` obniżono z 3500 do 1600 — inaczej prompt tury 2 nie mieściłby
się w kontekście. Realnie nic to nie ucina: mediana odpowiedzi Qry to 347
znaków, a p95 1437.

## Liczba parametrów nie przewiduje wyniku

| model | parametry | wynik | matematyka | kodowanie |
|---|---|---|---|---|
| Bielik 11B v3 | 11B | **7,53** | 9,06 | 6,55 |
| Bielik 4.5B v3 | 4,5B | **5,69** | 8,54 | 4,87 |
| Bielik 1.5B v3 | 1,5B | **3,83** | 6,02 | 2,87 |
| Qra-13B-chat | 13B | **3,30** | 2,05 | 1,53 |
| poziomka 09-14/1718 | ~4B | **1,40** | 0,95 | 0,05 |
| polanka 3.7B exp | 3,7B | **0,97** | 1,10 | 0,45 |

**Największy model w tabeli przegrywa z najmniejszym.** Qra ma 13B parametrów
i 3,30, Bielik 1,5B ma prawie dziewięć razy mniej i 3,83. W obrębie jednej
rodziny skala działa przewidywalnie — u Bielika każde potrojenie daje około
+1,85 — ale między rodzinami nie znaczy nic.

## Modele dzielą się na te, które liczą, i te, które piszą

Qra nie jest słaba językowo. Humanistyka 4,12, odgrywanie ról 4,03,
piśmiennictwo 3,90 i wnioskowanie 3,87 to wyniki lepsze niż u Bielika 1,5B
w tych samych kategoriach (odpowiednio 3,65, 4,00, 3,95 i 2,77). Cała jej strata
siedzi w zadaniach obliczeniowych: **matematyka 2,05 wobec 6,02, kodowanie 1,53
wobec 2,87**.

Ten podział przechodzi przez całą tabelę. Bieliki mają matematykę od 6,02 do
9,06. Qra 2,05. Poziomka i Polanka poniżej 1,3. To kategorie z referencjami,
gdzie sędzia sprawdza poprawność wyniku, a nie styl — i to one, a nie
polszczyzna, rozstrzygają o miejscu w tabeli.

Odsetek polszczyzny nie porządkuje modeli: Bielik 4,5B ma 97%, czyli więcej niż
11B (94%), przy wyniku niższym o 1,84. Dlatego ta statystyka nigdy nie wchodzi
do punktacji.

## Rozumowanie nie pomogło ani razu

Zmierzyliśmy oba warianty na trzech rodzinach i wyszły trzy różne mechanizmy,
ale ani jednego przypadku, w którym myślenie by pomogło.

| model | z myśleniem | bez myślenia | co się dzieje |
|---|---|---|---|
| poziomka 2026-09-14 (4 checkpointy) | 0,41–0,68 | **1,04–1,40** | zapętla się, nie domyka `</think>`, 42–62 pustych tur |
| poziomka 2026-09-09/0400 | 0,66 | 0,66 (mixed) | zapętla się rzadziej, ale wynik bez zmian |
| polanka 3.7B | 0,97 | 0,95 | rozumuje czysto w 95% tur, zero pustych, wynik ten sam |

**Polanka jest najczystszym przypadkiem.** Szablon z repo HF uruchamia
rozumowanie w 457 z 480 tur, model domyka blok za każdym razem — zero pustych
odpowiedzi, wobec 8 w wariancie bez myślenia. Nic się nie psuje po drodze,
a wynik stoi w miejscu: 0,97 wobec 0,95, przy rozrzucie sięgającym 0,19.
Matematyka wręcz **spadła** z 1,29 na 1,10 — czyli reasoning nie pomaga
dokładnie tam, gdzie powinien pomagać najbardziej.

## „mixed" — czego nie udało się zmierzyć

Szablon serii 2026-09-09 nie zna klucza `enable_thinking`, więc myślenia nie da się
w niej wyłączyć tak jak w serii 2026-09-14. Prefill — prompt kończący się zamkniętym blokiem
`<think></think>` — **zadziałał tylko w 47% tur**; w pozostałych 256 z 480 model
otworzył sobie własny blok mimo wszystko. Dlatego ten wiersz ma `mixed 53%`,
a nie `nie`, i nie wolno go zestawiać z wierszami `nie` z serii 2026-09-14.

Podobne zastrzeżenie dotyczy wiersza `polanka / compl. / tak`: szablon z repo HF
otwiera blok rozumowania, ale szablon w serwowanym katalogu tego nie robi. Ten
wiersz mierzy więc, czy Polanka **potrafi** skorzystać z rozumowania, a nie jak
zachowuje się domyślnie po wystawieniu.

## Cały przyrost serii 2026-09-14 mieści się między 800 a 1200 krokiem

| checkpoint | bez myślenia | zakres |
|---|---|---|
| `sft 2026-09-14/iter_0000400` | 1,04 | 0,95–1,13 |
| `sft 2026-09-14/iter_0000800` | 1,12 | 1,08–1,15 |
| `sft 2026-09-14/iter_0001200` | **1,40** | 1,30–1,46 |
| `sft 2026-09-14/iter_0001718` | **1,40** | 1,31–1,51 |

Od 400 do 800 zakresy zachodzą na siebie. Między 800 a 1200 jest skok o 0,28 przy
rozłącznych zakresach — jedyna realna poprawa w całej serii. Od 1200 do 1718
znowu nic. Z 1318 przebadanych kroków tylko okno 800–1200 cokolwiek wniosło.
