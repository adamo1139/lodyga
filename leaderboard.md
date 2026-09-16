# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | API | myślenie | przeb. | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v11/iter_0001200 | `/chat/completions` | nie | 3 | **1,40** | 1,30–1,46 | 0 | 90% | 2,50 | 2,01 | 1,62 | 1,25 | 0,17 | 0,57 | 0,83 | 2,27 |
| v11/iter_0001718 | `/chat/completions` | nie | 1 | **1,33** | 1,02–1,66 | 0 | 94% | 2,15 | 2,85 | 1,10 | 0,56 | 0,00 | 0,40 | 1,15 | 2,35 |
| v11/iter_0001718 | `/completions` | tak | 3 | **1,06** | 0,92–1,16 | 12 | 87% | 2,07 | 1,86 | 0,97 | 1,22 | 0,05 | 0,58 | 0,55 | 1,22 |
| v11/iter_0001718 | `/chat/completions` | tak | 1 | **0,70** | 0,45–0,97 | 49 | 67% | 1,05 | 0,53 | 0,30 | 1,00 | 0,55 | 0,90 | 0,25 | 1,00 |
| v11/iter_0001200 | `/chat/completions` | tak | 3 | **0,41** | 0,29–0,47 | 62 | 57% | 0,75 | 0,52 | 0,17 | 0,48 | 0,02 | 0,25 | 0,30 | 0,77 |

Kolumny kategorii: piśmiennictwo, odgrywanie ról, wnioskowanie, matematyka,
kodowanie, ekstrakcja, nauki ścisłe, humanistyka. „Puste" to tury, w których
model nie wygenerował odpowiedzi (na 160). „Pol." to odsetek odpowiedzi
rozpoznanych jako polskie — statystyka opisowa, nie składnik wyniku. „Rozrzut"
to zakres przebiegów tam, gdzie było ich kilka, a 95% przedział ufności tam,
gdzie był jeden.

Wszystkie wiersze to checkpointy SFT z `poziomka_sft_run2_v11_8192_hf`, z
identycznym samplingiem (`temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`, `max_tokens = 3500`) i tym samym sędzią
(`openai/gpt-5.6-luna`, `reasoning_effort = none`, `seed = 42`). Różni je tylko
to, co w kolumnach.

## Myślenie szkodzi obu checkpointom

| checkpoint | z myśleniem | bez myślenia |
|---|---|---|
| `iter_0001200` | 0,41 | **1,40** |
| `iter_0001718` | 0,70 | **1,33** |

Przy `iter_0001200` mamy po trzy przebiegi na wariant i zakresy nawet się nie
zbliżają: 0,29–0,47 wobec 1,30–1,46. Wyłączenie reasoningu podnosi wynik ponad
trzykrotnie i likwiduje wszystkie 62 puste odpowiedzi.

Przy `iter_0001200` wariant bez myślenia wygrywa **we wszystkich ośmiu
kategoriach**. Przy `iter_0001718` myślenie wygrywało jeszcze w matematyce,
ekstrakcji i kodowaniu — czyli tam, gdzie reasoning ma sens. Wcześniejszy
checkpoint nie ma nawet tego.

To nie jest wyłącznie efekt pustych tur. Licząc same niepuste odpowiedzi,
`iter_0001718` z myśleniem ma 0,83, a bez myślenia 1,33: nawet gdy model domknie
rozumowanie i odpowie, odpowiada gorzej niż wtedy, gdy nie myślał wcale.

Puste odpowiedzi biorą się z zapętlenia — model powtarza to samo zdanie w bloku
rozumowania i wyczerpuje limit tokenów, nie domykając `</think>`. Stąd też spadki
odsetka polszczyzny do 57–67%: część odpowiedzi to puste stringi.

## Co zmienia dłuższy trening

Bez myślenia oba checkpointy są nierozróżnialne (1,40 wobec 1,33, w granicach
rozrzutu). Z myśleniem późniejszy `iter_0001718` wypada lepiej od `iter_0001200`
(0,70 wobec 0,41), a liczba pustych odpowiedzi spada z 62 do 49. Wygląda to tak,
jakby dłuższy trening uczył głównie domykania rozumowania, a nie odpowiadania
lepiej.

Tura 2 wypada gorzej od tury 1 we wszystkich konfiguracjach (np. 1,63 → 1,17 przy
`iter_0001200` bez myślenia): model gubi wątek przy pytaniu uzupełniającym.
