# Łodyga - polski MT-Bench bazowany na implementacji SpeakLeash.

Oceniaj polskie modele instruct na 80 pytaniach w dwóch turach.

```bash
cp .env.example .env
./lodyga.py run --config config.poziomka.toml --judge config.judge.example.toml
```

W `.env` wpisz klucz do OpenRouter, a w kopii `config.example.toml` swój
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

Cały protokół opisuje [`custom_scoring.md`](custom_scoring.md).
