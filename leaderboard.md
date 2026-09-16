# Wyniki

Skala 0–10, średnia ze wszystkich ocenionych tur. Protokół opisuje
[`custom_scoring.md`](custom_scoring.md).

**To nie są wyniki porównywalne z leaderboardem SpeakLeash** — inny sędzia, inna
rubryka, inne prompty. Porównuj tylko wiersze z tej tabeli między sobą.

| model | wynik | rozrzut | puste | pol. | piśm. | role | wnios. | mat. | kod. | ekstr. | ścisłe | human. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| poziomka_iter_0001718_chat_nothink | **1,33** | 1,02–1,66 | 0 | 94% | 2,15 | **2,85** | 1,10 | 0,56 | 0,00 | 0,40 | 1,15 | **2,35** |
| poziomka_iter_0001718 | **1,06** | 0,92–1,16 | 12 | 87% | 2,07 | 1,86 | 0,97 | **1,22** | 0,05 | 0,58 | 0,55 | 1,22 |
| poziomka_iter_0001718_chat_think | **0,70** | 0,45–0,97 | 49 | 67% | 1,05 | 0,53 | 0,30 | 1,00 | **0,55** | **0,90** | 0,25 | 1,00 |

Kolumny: piśmiennictwo, odgrywanie ról, wnioskowanie, matematyka, kodowanie,
ekstrakcja, nauki ścisłe, humanistyka. „Puste" to tury, w których model nie
wygenerował odpowiedzi (na 160). „Pol." to odsetek odpowiedzi rozpoznanych jako
polskie — statystyka opisowa, nie składnik wyniku.

Rozrzut dla `poziomka_iter_0001718` to zakres trzech przebiegów; dla pozostałych
95% przedział ufności z jednego przebiegu.

## Czym te trzy wiersze się różnią

To jeden checkpoint SFT `poziomka_sft_run2_v11_8192_hf/iter_0001718` w trzech
konfiguracjach. Generowanie: `temperature = 0,9`, `top_p = 0,9`, `top_k = 40`,
`repetition_penalty = 1,05`, `max_tokens = 3500`. Sędzia: `openai/gpt-5.6-luna`,
`reasoning_effort = none`, `seed = 42`.

| wiersz | API | myślenie | przebiegi |
|---|---|---|---|
| `poziomka_iter_0001718` | `/completions` | włączone | 3, uśrednione |
| `poziomka_iter_0001718_chat_think` | chat | włączone | 1 |
| `poziomka_iter_0001718_chat_nothink` | chat | wyłączone | 1 |

**Wiersza z `/completions` nie porównuj wprost z dwoma pozostałymi** — inna
ścieżka API i trzy przebiegi zamiast jednego. Uczciwe jest tylko zestawienie
`chat_think` z `chat_nothink`, bo różni je wyłącznie `enable_thinking`.

## Myślenie szkodzi temu checkpointowi

Wyłączenie reasoningu podniosło wynik z 0,70 do 1,33 i zlikwidowało wszystkie 49
pustych odpowiedzi. To nie jest wyłącznie efekt tych pustych tur: licząc same
niepuste odpowiedzi, `chat_think` ma 0,83, a `chat_nothink` 1,33. Nawet gdy model
domknie rozumowanie i odpowie, odpowiada gorzej niż wtedy, gdy nie myślał wcale.

Reasoning pomaga tylko tam, gdzie trzeba coś policzyć lub wyciągnąć z tekstu:
matematyka (+0,44), ekstrakcja (+0,50), kodowanie (+0,55). W pozostałych pięciu
kategoriach szkodzi, najmocniej przy odgrywaniu ról (0,53 wobec 2,85) — model
zamiast wejść w rolę, rozmyśla nad tym, jak w nią wejść.

Puste odpowiedzi biorą się z zapętlenia: model powtarza to samo zdanie w bloku
rozumowania i wyczerpuje limit tokenów, nie domykając `</think>`. Stąd też spadek
odsetka polszczyzny do 67% — jedna trzecia odpowiedzi to puste stringi.

Tura 2 wypada gorzej od tury 1 we wszystkich trzech konfiguracjach (np. 1,54 → 1,12
przy `chat_nothink`): model gubi wątek przy pytaniu uzupełniającym.

Wszystkie liczby pochodzą z jednego przebiegu na wariant (poza pierwszym
wierszem), więc drobne różnice są w granicach szumu. Kierunek „myślenie szkodzi"
jest jednak znacznie większy niż zaobserwowany rozrzut między przebiegami
(±0,12), więc na pewno nie jest przypadkiem.
