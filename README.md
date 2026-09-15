# Łodyga — polski MT-Bench

Ocenia polskie modele czatowe na 80 pytaniach w dwóch turach. Protokół — rubryka,
prompty sędziego, przebiegi, agregacja, detekcja języka — jest w
[`custom_scoring.md`](custom_scoring.md). To nowa ewaluacja, nie odtworzenie rankingu SpeakLeash.

```bash
cp .env.example .env && chmod 600 .env    # wpisz OPENROUTER_API_KEY
./lodyga.py run --config config.poziomka.toml --judge config.judge.example.toml
```

Skopiuj `config.example.toml` dla każdego modelu. `run` generuje, ocenia i zapisuje
wynik do katalogu ze znacznikiem czasu w `data/mt_bench/runs/`: odpowiedzi, oceny,
surowe archiwum sędziego, raport i użyte konfiguracje; nic nie jest nadpisywane.
`--passes N` uśrednia powtórzone przebiegi. Zobacz `./lodyga.py --help`.

Pytania: [speakleash/mt-bench-pl](https://huggingface.co/spaces/speakleash/mt-bench-pl),
MT-Bench po polsku; źródło podaje `license: other` — sprawdź warunki przed redystrybucją.
`app.py`, `common.py`, `content.py`, `src/` to nieużywany kod z oryginalnego Space.
