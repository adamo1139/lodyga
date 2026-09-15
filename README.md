# Łodyga — polski MT-Bench bazowany na implementacji SpeakLeash.

Oceniaj polskie modele instruct na 80 pytaniach w dwóch turach.

```bash
cp .env.example .env
./lodyga.py run --config config.poziomka.toml --judge config.judge.example.toml
```

W `.env` wpisz klucz do OpenRouter, a w kopii `config.example.toml` swój
endpoint. Jedna komenda generuje odpowiedzi, ocenia je i liczy wynik. Wszystko
ląduje w `data/mt_bench/runs/`, w katalogu z datą w nazwie, więc nic się nie
nadpisuje. `--passes N` powtarza ewaluację i uśrednia wyniki, a `--help`
pokazuje resztę komend.

Cały protokół opisuje [`custom_scoring.md`](custom_scoring.md).

Pytania pochodzą z [speakleash/mt-bench-pl](https://huggingface.co/spaces/speakleash/mt-bench-pl)
i są tłumaczeniem MT-Bench. Licencja źródła to `other`, więc sprawdź warunki
przed publikacją.
