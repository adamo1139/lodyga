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
| v11/iter_0000800 | `/chat/completions` | tak | 3 | **0,68** | 0,62–0,71 | 42 | 70% | 1,17 | 0,51 | 0,37 | 0,99 | 0,23 | 0,33 | 0,38 | 1,42 |
| v11/iter_0001718 | `/chat/completions` | tak | 3 | **0,59** | 0,55–0,63 | 45 | 69% | 1,08 | 0,41 | 0,37 | 0,79 | 0,02 | 0,45 | 0,53 | 1,08 |
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
| `iter_0000800` | 0,68 | **1,12** | 42 |
| `iter_0001200` | 0,41 | **1,40** | 62 |
| `iter_0001718` | 0,59 | **1,40** | 45 |

Po trzy przebiegi na wariant, zakresy nigdzie się nie stykają. Wyłączenie
reasoningu podnosi wynik wszędzie i za każdym razem likwiduje **wszystkie** puste
odpowiedzi.

To nie jest wyłącznie efekt pustych tur. Licząc same niepuste odpowiedzi,
`iter_0001718` z myśleniem miał 0,83 wobec 1,33 bez myślenia: nawet gdy model
domknie rozumowanie i odpowie, odpowiada gorzej niż wtedy, gdy nie myślał wcale.

Puste odpowiedzi biorą się z zapętlenia — model powtarza to samo zdanie w bloku
rozumowania i wyczerpuje limit tokenów, nie domykając `</think>`. Stąd też spadki
odsetka polszczyzny do 57–70%: część odpowiedzi to puste stringi.

## Krzywa treningu jest płaska po 1200 kroku

Bez myślenia, czyli w wariancie, który wypada najlepiej:

| checkpoint | wynik | zakres |
|---|---|---|
| `iter_0000800` | 1,12 | 1,08–1,15 |
| `iter_0001200` | **1,40** | 1,30–1,46 |
| `iter_0001718` | **1,40** | 1,31–1,51 |

Między 800 a 1200 krokiem jest realny przyrost (zakresy się nie stykają). Między
1200 a 1718 nie ma **żadnego** — te same 1,40 i zachodzące na siebie zakresy.
Pięćset kroków więcej nie dało nic.

W wariancie z myśleniem kolejność jest wręcz nieuporządkowana: 0,68 przy 800,
potem spadek do 0,41 przy 1200 i 0,59 przy 1718. Liczba pustych odpowiedzi też
skacze (42 → 62 → 45) zamiast maleć. Zdolność do domknięcia rozumowania nie
poprawia się monotonicznie wraz z treningiem.

Tura 2 wypada gorzej od tury 1 we wszystkich konfiguracjach: model gubi wątek
przy pytaniu uzupełniającym.
