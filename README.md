# Łodyga - polski MT-Bench bazowany na implementacji SpeakLeash.

80 pytań po polsku, w ośmiu kategoriach po dziesięć: piśmiennictwo, odgrywanie
ról, wnioskowanie, matematyka, kodowanie, ekstrakcja, nauki ścisłe i
humanistyka. Każde ma drugą turę, która nawiązuje do pierwszej odpowiedzi.
Połowa pytań ma wzorcową odpowiedź, którą dostaje sędzia LLM.

```bash
cp .env.example .env
./lodyga.py run --config configs/config.poziomka.toml --judge configs/config.judge.example.toml
```

W `.env` wpisz klucz do OpenRouter, a w kopii `configs/config.example.toml` swój
endpoint. Jedna komenda generuje odpowiedzi, ocenia je i liczy wynik. Wszystko
ląduje w `data/mt_bench/runs/`.

```
usage: lodyga run [-h] --config CONFIG [--concurrency CONCURRENCY]
                  [--judge JUDGE] [--judge-concurrency JUDGE_CONCURRENCY]
                  [--iterations ITERATIONS] [--seed SEED] [--passes PASSES]

options:
  -h, --help            show this help message and exit
  --config CONFIG       model config TOML
  --concurrency CONCURRENCY
                        questions generated at once
  --judge JUDGE         judge config TOML
  --judge-concurrency JUDGE_CONCURRENCY
                        turns judged at once
  --iterations ITERATIONS
                        bootstrap iterations
  --seed SEED           bootstrap seed
  --passes PASSES       repeat the whole evaluation N times and average;
                        default 1
```

## Zanim puścisz pomiar

```
python3 sonda.py
```

Kilkadziesiąt zapytań w kilkanaście sekund. Sprawdza, czy model nie jest
zepsuty (zepsuty merge zwraca same znaki zastępcze - wykrywamy to przy
`temperature = 0`, bo greedy nie ma losowości), czy szablon respektuje
`enable_thinking`, jaki `max_tokens` mieści się w oknie serwera i która
temperatura daje mniej urwanych oraz zapętlonych tur.

Sonda odsiewa katastrofy i dobiera parametry. Liczb do tabeli z niej nie bierz:
przy 16 pytaniach wychodziło 0 zapętlonych tur tam, gdzie pełny przebieg
pokazał 13% z 480.

Cały protokół opisuje [`custom_scoring.md`](custom_scoring.md), a wyniki
zmierzonych modeli zbiera [`leaderboard.md`](leaderboard.md).
