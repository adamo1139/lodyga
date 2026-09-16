# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | API | myślenie | przeb. | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v11/iter_0001718 | `/chat/completions` | nie | 3 | **1,40** | 1,31–1,51 | 0 | 93% | 2,28 | 2,09 | 1,75 | 0,95 | 0,05 | 0,77 | 1,25 | 2,12 |
| v11/iter_0001200 | `/chat/completions` | nie | 3 | **1,40** | 1,30–1,46 | 0 | 90% | 2,50 | 2,01 | 1,62 | 1,25 | 0,17 | 0,57 | 0,83 | 2,27 |
| v11/iter_0000800 | `/chat/completions` | nie | 3 | **1,12** | 1,08–1,15 | 0 | 94% | 2,24 | 1,88 | 0,82 | 0,50 | 0,18 | 0,28 | 0,81 | 2,22 |
| v11/iter_0001718 | `/completions` | tak | 3 | **1,06** | 0,92–1,16 | 12 | 87% | 2,07 | 1,86 | 0,97 | 1,22 | 0,05 | 0,58 | 0,55 | 1,22 |
| v11/iter_0000400 | `/chat/completions` | nie | 3 | **1,04** | 0,95–1,13 | 0 | 90% | 2,12 | 1,62 | 0,95 | 0,60 | 0,05 | 0,53 | 0,80 | 1,60 |
| v11/iter_0000800 | `/chat/completions` | tak | 3 | **0,68** | 0,62–0,71 | 42 | 70% | 1,17 | 0,51 | 0,37 | 0,99 | 0,23 | 0,33 | 0,38 | 1,42 |
| v11/iter_0001718 | `/chat/completions` | tak | 3 | **0,59** | 0,55–0,63 | 45 | 69% | 1,08 | 0,41 | 0,37 | 0,79 | 0,02 | 0,45 | 0,53 | 1,08 |
| v11/iter_0000400 | `/chat/completions` | tak | 3 | **0,50** | 0,45–0,57 | 50 | 65% | 1,07 | 0,38 | 0,33 | 0,51 | 0,40 | 0,40 | 0,10 | 0,83 |
| v11/iter_0001200 | `/chat/completions` | tak | 3 | **0,41** | 0,29–0,47 | 62 | 57% | 0,75 | 0,52 | 0,17 | 0,48 | 0,02 | 0,25 | 0,30 | 0,77 |

Kolumny kategorii: piśmiennictwo, odgrywanie ról, wnioskowanie, matematyka,
kodowanie, ekstrakcja, nauki ścisłe, humanistyka. „Puste" to tury, w których
model nie wygenerował odpowiedzi (na 160). „Pol." to odsetek odpowiedzi
rozpoznanych jako polskie — statystyka opisowa, nie składnik wyniku. „Rozrzut"
to zakres wyników z kolejnych przebiegów.

Wszystkie wiersze to checkpointy SFT z `poziomka_sft_run2_v11_8192_hf`, z
identycznym samplingiem (`temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`, `max_tokens = 3500`) i tym samym sędzią
(`openai/gpt-5.6-luna`, `reasoning_effort = none`, `seed = 42`). Różni je tylko
to, co w kolumnach.

## Myślenie szkodzi każdemu checkpointowi

| checkpoint | z myśleniem | bez myślenia | puste (z myśl.) |
|---|---|---|---|
| `iter_0000400` | 0,50 | **1,04** | 50 |
| `iter_0000800` | 0,68 | **1,12** | 42 |
| `iter_0001200` | 0,41 | **1,40** | 62 |
| `iter_0001718` | 0,59 | **1,40** | 45 |

Cztery checkpointy, po trzy przebiegi na wariant, i za każdym razem to samo:
wyłączenie reasoningu podnosi wynik dwukrotnie lub więcej i likwiduje
**wszystkie** puste odpowiedzi. Zakresy nigdzie się nie stykają.

To nie jest wyłącznie efekt pustych tur. Licząc same niepuste odpowiedzi,
`iter_0001718` z myśleniem miał 0,83 wobec 1,33 bez myślenia: nawet gdy model
domknie rozumowanie i odpowie, odpowiada gorzej niż wtedy, gdy nie myślał wcale.

Puste odpowiedzi biorą się z zapętlenia — model powtarza to samo zdanie w bloku
rozumowania i wyczerpuje limit tokenów, nie domykając `</think>`. Stąd też spadki
odsetka polszczyzny do 57–70%: część odpowiedzi to puste stringi.

## Cały przyrost mieści się między 800 a 1200 krokiem

Bez myślenia, czyli w wariancie, który wypada najlepiej:

| checkpoint | wynik | zakres |
|---|---|---|
| `iter_0000400` | 1,04 | 0,95–1,13 |
| `iter_0000800` | 1,12 | 1,08–1,15 |
| `iter_0001200` | **1,40** | 1,30–1,46 |
| `iter_0001718` | **1,40** | 1,31–1,51 |

Od 400 do 800 kroku zakresy zachodzą na siebie, więc przyrostu nie widać. Między
800 a 1200 jest skok o 0,28 przy rozłącznych zakresach — jedyna realna poprawa
w całej serii. Od 1200 do 1718 znowu nic: ten sam wynik 1,40 i zachodzące
zakresy.

Innymi słowy, z 1318 przebadanych kroków treningu tylko okno 800–1200 cokolwiek
wniosło. Ani wcześniejsze 800 kroków, ani późniejsze 518 nie zmieniły wyniku.

W wariancie z myśleniem kolejność jest nieuporządkowana: 0,50 → 0,68 → 0,41 →
0,59. Liczba pustych odpowiedzi skacze (50 → 42 → 62 → 45) zamiast maleć.
Zdolność do domknięcia rozumowania nie poprawia się wraz z treningiem.

Tura 2 wypada gorzej od tury 1 we wszystkich konfiguracjach: model gubi wątek
przy pytaniu uzupełniającym.
