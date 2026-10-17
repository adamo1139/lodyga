# Wyniki w podziale na tury

Skala 0–10, średnia z 3 przebiegów. Liczby z `judgments.jsonl` tych samych
przebiegów, które stoją za wierszami w [`leaderboard.md`](leaderboard.md).

| | cpral/poziomka-instruct-2026-10-10 | poziomka-instruct-2026-10-13-della | run14 destylacja | 09-30-7 (8k) z rozumowaniem | Bielik-1.5B-v3-Instruct | cpral/instruktor-lotnictwa-7B-2-hf | Muse-Glimmer-30B |
|---|---|---|---|---|---|---|---|
| **wynik ogólny** | **2,12** | **2,13** | **2,09** | **1,41** | **3,83** | **5,29** | **8,18** |
| tura 1 | 2,52 | 2,48 | 2,44 | 1,83 | 4,24 | 5,77 | 8,64 |
| tura 2 | 1,71 | 1,79 | 1,74 | 0,98 | 3,43 | 4,80 | 7,72 |
| spadek | −0,81 | −0,69 | −0,70 | −0,86 | −0,80 | −0,97 | −0,92 |

## Tura 1

| kategoria | cpral/poziomka-instruct-2026-10-10 | poziomka-instruct-2026-10-13-della | run14 destylacja | 09-30-7 (8k) z rozumowaniem | Bielik-1.5B-v3-Instruct | cpral/instruktor-lotnictwa-7B-2-hf | Muse-Glimmer-30B |
|---|---|---|---|---|---|---|---|
| piśmiennictwo | 5,37 | 4,53 | 4,27 | 3,67 | 5,21 | 7,30 | 8,60 |
| odgrywanie ról | 3,96 | 2,93 | 3,60 | 2,43 | 3,97 | 5,47 | 8,10 |
| wnioskowanie | 2,13 | 1,80 | 1,73 | 1,27 | 2,20 | 4,90 | 9,23 |
| matematyka | 2,03 | 2,47 | 2,37 | 2,20 | 7,29 | 8,29 | 9,83 |
| kodowanie | 0,43 | 1,19 | 1,43 | 0,40 | 3,33 | 3,07 | 8,73 |
| ekstrakcja | 1,10 | 1,10 | 0,63 | 1,27 | 4,61 | 6,00 | 9,03 |
| nauki ścisłe | 2,58 | 2,67 | 2,43 | 2,10 | 3,93 | 6,03 | 7,83 |
| humanistyka | 2,67 | 3,10 | 3,07 | 1,33 | 3,63 | 5,23 | 7,77 |

## Tura 2

| kategoria | cpral/poziomka-instruct-2026-10-10 | poziomka-instruct-2026-10-13-della | run14 destylacja | 09-30-7 (8k) z rozumowaniem | Bielik-1.5B-v3-Instruct | cpral/instruktor-lotnictwa-7B-2-hf | Muse-Glimmer-30B |
|---|---|---|---|---|---|---|---|
| piśmiennictwo | 1,87 | 1,67 | 1,43 | 1,20 | 2,73 | 5,23 | 5,67 |
| odgrywanie ról | 3,56 | 3,86 | 3,20 | 2,07 | 4,03 | 5,90 | 7,63 |
| wnioskowanie | 1,80 | 1,57 | 1,80 | 0,73 | 3,33 | 4,63 | 7,77 |
| matematyka | 0,69 | 0,93 | 1,00 | 0,44 | 4,74 | 5,53 | 9,47 |
| kodowanie | 0,37 | 0,70 | 0,90 | 0,20 | 2,40 | 2,63 | 8,80 |
| ekstrakcja | 0,97 | 1,23 | 0,80 | 1,00 | 3,73 | 5,23 | 8,73 |
| nauki ścisłe | 1,63 | 1,53 | 2,17 | 0,63 | 2,83 | 3,53 | 6,57 |
| humanistyka | 2,97 | 2,87 | 2,63 | 1,50 | 3,67 | 5,73 | 7,17 |

## Czym są te modele

- **cpral/poziomka-instruct-2026-10-10** — merge Arcee Fusion checkpointów SFT,
  bez rozumowania. Ma NAJWYŻSZE wśród wszystkich mierzonych Poziomek bez
  rozumowania piśmiennictwo (3,62) i odgrywanie ról (3,75).
  Sampler: `max_tokens 7800 / t0,6 / top_p 0,9 / min_p 0,05 / fp 0,15`.
- **poziomka-instruct-2026-10-13-della** — DELLA z merge'ów 10-10 i trajektorii
  run11, baza 09-30-7, bez rozumowania. Ten sam sampler.
- **run14 destylacja** — `poziomka kd run14/iter_0000635`, destylacja wiedzy
  (odwrotna dywergencja KL po top-40 logitach), punkt startowy to run13
  (`cpral/uczen-lotnictwa-4b-2-hf`), bez rozumowania. Ten sam sampler.
- **09-30-7 (8k) z rozumowaniem** — NAJLEPSZY wynik ogólny wśród wszystkich
  mierzonych Poziomek Z ROZUMOWANIEM (1,41). Okno 8192, RoPE 84000. To inny
  wariant tego samego modelu, który jest bazą run13 i run14.
- **Bielik-1.5B-v3-Instruct** — `speakleash/Bielik-1.5B-v3-Instruct`, bez
  dotrenowania, nie rozumuje.
- **cpral/instruktor-lotnictwa-7B-2-hf** — `Bielik-PL-Minitron-7B-v3.0-Instruct`
  dotrenowany na `nauka_lotnictwa_2`, bez rozumowania.
  Sampler: `max_tokens 3500 / t0,9 / top_p 0,9 / top_k 40 / rep 1,05`.
- **Muse-Glimmer-30B** — model zewnętrzny, dla skali, rozumuje (systemowe
  `Reasoning strength: low`). Sampler: `max_tokens 3500 / t1,0 / top_p 0,95 /
  top_k 64`.

Samplery NIE są wspólne dla wszystkich kolumn — każdy model mierzony jest tym,
który dla niego dobrano. Dwie kolumny ROZUMUJĄ (09-30-7 i Muse-Glimmer),
pozostałe pięć nie, więc to nie jest porównanie równych warunków.
