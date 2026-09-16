# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | API | myślenie | przeb. | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bielik-4.5B-v3-Instruct | chat | brak | 3 | **5,69** | 5,60–5,86 | 0 | 97% | 4,77 | 5,73 | 5,35 | 8,54 | 4,87 | 5,85 | 5,03 | 5,55 |
| poziomka v11/iter_0001718 | chat | nie | 3 | **1,40** | 1,31–1,51 | 0 | 93% | 2,28 | 2,09 | 1,75 | 0,95 | 0,05 | 0,77 | 1,25 | 2,12 |
| poziomka v11/iter_0001200 | chat | nie | 3 | **1,40** | 1,30–1,46 | 0 | 90% | 2,50 | 2,01 | 1,62 | 1,25 | 0,17 | 0,57 | 0,83 | 2,27 |
| poziomka v11/iter_0000800 | chat | nie | 3 | **1,12** | 1,08–1,15 | 0 | 94% | 2,24 | 1,88 | 0,82 | 0,50 | 0,18 | 0,28 | 0,81 | 2,22 |
| poziomka v11/iter_0001718 | compl. | tak | 3 | **1,06** | 0,92–1,16 | 12 | 87% | 2,07 | 1,86 | 0,97 | 1,22 | 0,05 | 0,58 | 0,55 | 1,22 |
| poziomka v11/iter_0000400 | chat | nie | 3 | **1,04** | 0,95–1,13 | 0 | 90% | 2,12 | 1,62 | 0,95 | 0,60 | 0,05 | 0,53 | 0,80 | 1,60 |
| poziomka v11/iter_0000800 | chat | tak | 3 | **0,68** | 0,62–0,71 | 42 | 70% | 1,17 | 0,51 | 0,37 | 0,99 | 0,23 | 0,33 | 0,38 | 1,42 |
| poziomka 0909/iter_0000400 | compl. | mixed 53% | 3 | **0,66** | 0,62–0,72 | 0 | 94% | 1,35 | 0,85 | 0,68 | 0,63 | 0,15 | 0,22 | 0,53 | 0,92 |
| poziomka 0909/iter_0000400 | compl. | tak | 3 | **0,66** | 0,61–0,71 | 22 | 80% | 1,33 | 0,98 | 0,85 | 0,46 | 0,07 | 0,27 | 0,28 | 1,03 |
| poziomka v11/iter_0001718 | chat | tak | 3 | **0,59** | 0,55–0,63 | 45 | 69% | 1,08 | 0,41 | 0,37 | 0,79 | 0,02 | 0,45 | 0,53 | 1,08 |
| poziomka v11/iter_0000400 | chat | tak | 3 | **0,50** | 0,45–0,57 | 50 | 65% | 1,07 | 0,38 | 0,33 | 0,51 | 0,40 | 0,40 | 0,10 | 0,83 |
| poziomka v11/iter_0001200 | chat | tak | 3 | **0,41** | 0,29–0,47 | 62 | 57% | 0,75 | 0,52 | 0,17 | 0,48 | 0,02 | 0,25 | 0,30 | 0,77 |

Kolumny kategorii: piśmiennictwo, odgrywanie ról, wnioskowanie, matematyka,
kodowanie, ekstrakcja, nauki ścisłe, humanistyka. „Puste" to tury, w których
model nie wygenerował odpowiedzi (na 160). „Pol." to odsetek odpowiedzi
rozpoznanych jako polskie — statystyka opisowa, nie składnik wyniku. „Rozrzut"
to zakres wyników z kolejnych przebiegów. API: `chat` to `/chat/completions`,
`compl.` to `/completions` z szablonem renderowanym lokalnie. „Myślenie: brak"
oznacza model, który w ogóle nie ma reasoningu w szablonie czatu.

Sampling identyczny wszędzie (`temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`, `max_tokens = 3500`), sędzia też
(`openai/gpt-5.6-luna`, `reasoning_effort = none`, `seed = 42`).

## Bielik 4.5B jest cztery razy lepszy od najlepszej Poziomki

| | Bielik 4.5B v3 | poziomka v11/1718 bez myśl. |
|---|---|---|
| wynik | **5,69** | 1,40 |
| matematyka | **8,54** | 0,95 |
| kodowanie | **4,87** | 0,05 |
| polszczyzna | 97% | 93% |
| tura 2 / tura 1 | 0,81 | 0,70 |

Największa przepaść jest w kategoriach z referencjami, czyli tam, gdzie sędzia
sprawdza poprawność, a nie styl: matematyka 8,54 wobec 0,95 i kodowanie 4,87
wobec 0,05. Poziomka nie tyle pisze gorzej, co **nie rozwiązuje zadań**.

Bielik ma też najrówniejszy profil w tabeli — wszystkie kategorie między 4,77
a 8,54, bez ani jednej zapaści. Poziomka rozciąga się od 0,05 do 2,50.

Dla samego benchmarku jest to dobra wiadomość: skala 0–10 realnie się rozciąga,
a niskie wyniki Poziomki nie są artefaktem zbyt surowego sędziego.

## „mixed" — czego nie udało się zmierzyć

Szablon serii 0909 nie zna klucza `enable_thinking`, więc myślenia nie da się
w niej wyłączyć tak jak w v11. Prefill — prompt kończący się zamkniętym blokiem
`<think></think>` — **zadziałał tylko w 47% tur**; w pozostałych 256 z 480 model
otworzył sobie własny blok mimo wszystko. Dlatego ten wiersz ma `mixed 53%`,
a nie `nie`, i nie wolno go zestawiać z wierszami `nie` z serii v11.

## Myślenie szkodzi każdemu checkpointowi v11

| checkpoint | z myśleniem | bez myślenia | puste (z myśl.) |
|---|---|---|---|
| `v11/iter_0000400` | 0,50 | **1,04** | 50 |
| `v11/iter_0000800` | 0,68 | **1,12** | 42 |
| `v11/iter_0001200` | 0,41 | **1,40** | 62 |
| `v11/iter_0001718` | 0,59 | **1,40** | 45 |

Wszędzie wyłączenie reasoningu podnosi wynik dwukrotnie lub więcej i likwiduje
wszystkie puste odpowiedzi; zakresy nigdzie się nie stykają. To nie jest wyłącznie
efekt pustych tur: licząc same niepuste odpowiedzi, `v11/iter_0001718`
z myśleniem miał 0,83 wobec 1,33 bez myślenia.

U serii 0909 jest inaczej: wyzerowanie pustych tur i skok polszczyzny z 80% na
94% **nie zmieniły wyniku ani o setną** (0,66 w obu wariantach). Tam ogranicza
nie zapętlanie się, tylko jakość samych odpowiedzi.

## Cały przyrost v11 mieści się między 800 a 1200 krokiem

| checkpoint | bez myślenia | zakres |
|---|---|---|
| `v11/iter_0000400` | 1,04 | 0,95–1,13 |
| `v11/iter_0000800` | 1,12 | 1,08–1,15 |
| `v11/iter_0001200` | **1,40** | 1,30–1,46 |
| `v11/iter_0001718` | **1,40** | 1,31–1,51 |

Od 400 do 800 zakresy zachodzą na siebie. Między 800 a 1200 jest skok o 0,28 przy
rozłącznych zakresach — jedyna realna poprawa w całej serii. Od 1200 do 1718
znowu nic. Z 1318 przebadanych kroków tylko okno 800–1200 cokolwiek wniosło.

Tura 2 wypada gorzej od tury 1 we wszystkich konfiguracjach: model gubi wątek
przy pytaniu uzupełniającym. Najłagodniej u Bielika (0,81), najostrzej
u Poziomki (~0,70).
