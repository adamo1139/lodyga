#!/usr/bin/env python3
"""Dobór samplera pod domykanie bloku rozumowania.

Sonda (`sonda.py`) odpowiada na pytanie, czy model da się w ogóle mierzyć. Ten
skrypt odpowiada na inne: którym samplerem. Dotyczy to przede wszystkim
wariantów z rozumowaniem, gdzie wąskim gardłem nie jest jakość, a wyjście
z bloku `<think>` w budżecie tokenów - tura bez domkniętego `</think>` nie ma
odpowiedzi i liczy się jako pusta.

Miarą jest udział tur z niepustą odpowiedzią, osobno dla tury 1 i tury 2.

DWIE RZECZY, KTÓRE MUSZĄ ZOSTAĆ, bo każda wzięła się z pomyłki:

1. Mierzymy OBIE TURY. Prompt tury 2 zawiera odpowiedź z tury 1, więc na ślad
   i odpowiedź zostaje mniej z budżetu. Sonda na samej turze 1 zapowiadała dla
   run6 ~15% pustych tur, a pełny przebieg dał 43%.
   Tura 2 NIE jest jednak gorsza zawsze: na run7 i merge'u SCE wypadała około
   dwa razy gorzej, ale na run10, który odpowiada krótko (mediana 575 znaków),
   wyszła tak samo jak tura 1 (28/32 i 28/32) - a przy złym samplerze wzór
   wracał (`t0,8 fp0,15`: 21/32 wobec 16/32, ślad 12 201 znaków). Różnicy między
   turami nie zakładaj, zmierz ją.

2. 32 PRÓBY NA WARIANT, nie 16. Na 16 pytaniach ten sam zestaw dawał raz 15/16,
   raz 11/16 - rozrzut między powtórzeniami był tak duży jak różnice między
   samplerami. Stąd domyślne `--proby 2` (każde pytanie dwa razy).

CO TEN SKRYPT MIERZY, A CZEGO NIE. Mierzy mechanikę: domykanie bloku, urwane
tury, długości. NIE mierzy jakości tekstu - a `frequency_penalty` i temperatura
wpływają też na zwięzłość i powtarzalność sformułowań, co widzi tylko sędzia.
Do wyboru samplera w wariancie BEZ rozumowania ten skrypt jest więc za słaby;
tam trzeba porównać ocenione przebiegi.

CO DOTĄD WYSZŁO (wszystkie na 32 próbach, udział tur z odpowiedzią tura 1/tura 2):

    model                      fp0,05          fp0,15
    run7 (v13, gbs16)          27/32  21/32    17/32  16/32
    merge SCE 2026-10-07       29/32  19/32    15/32  13/32
    run10 (v4, gbs16)          28/32  28/32    22/32  21/32

Decyduje kara, nie temperatura: przy ustalonym `fp` temperatury 0,6/0,8/1,0 dają
wyniki w granicach szumu. Zależność od kary jest niemonotoniczna - zero jest złe
(model kręci się w śladzie i wyczerpuje budżet), około 0,05 najlepsze, od 0,15
w górę coraz gorzej. Przyczyna: `</think>` to pięć zwykłych tokenów APT4, nie
znacznik specjalny, więc kara za powtórzenia tłumi je jak każdy inny powtórzony
token. Z tego samego powodu serwer wymaga `--grammar-backend none`.

UWAGA: `frequency_penalty = 0.0` i pominięcie tego pola dawały RÓŻNE wyniki, choć
domyślna wartość to zero. Nie traktuj ich jak synonimów.

Użycie:
    python3 sampler.py --config configs/config.poziomka.run10-v4-gbs16-ctx16k.toml
    python3 sampler.py --config ... --temperatury 0.6 1.0 --kary 0.05 0.15
    python3 sampler.py --config ... --proby 1 --pytania 8      # szybki podgląd
"""

import argparse
import itertools
import json
import statistics
import time
import tomllib
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import sonda


def zapytaj(cfg, gen, wiadomosci, think):
    """Jedna tura przez /chat/completions; zwraca (finish, ślad, odpowiedź)."""
    api = cfg["api"]
    payload = {"model": cfg["_model"], "messages": wiadomosci, **gen}
    if think is not None:
        payload["chat_template_kwargs"] = {"enable_thinking": think}
    req = urllib.request.Request(
        api["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=api.get("timeout", 900)) as odp:
        wybor = json.load(odp)["choices"][0]
    wiadomosc = wybor["message"]
    slad = wiadomosc.get("reasoning_content") or wiadomosc.get("reasoning") or ""
    return wybor.get("finish_reason"), slad, (wiadomosc.get("content") or "").strip()


def rozmowa(cfg, gen, pytanie, think):
    """Obie tury po kolei.

    Tura 2 dostaje TYLKO odpowiedź z tury 1, bez śladu rozumowania - tak samo jak
    w `generate_answers.py`. Gdyby ślad wchodził do kontekstu, budżet tury 2
    wyglądałby inaczej niż w pomiarze.
    """
    pierwsza = zapytaj(cfg, gen, [{"role": "user", "content": pytanie["turns"][0]}], think)
    druga = zapytaj(cfg, gen, [
        {"role": "user", "content": pytanie["turns"][0]},
        {"role": "assistant", "content": pierwsza[2]},
        {"role": "user", "content": pytanie["turns"][1]},
    ], think)
    return pierwsza, druga


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", type=Path, required=True,
                        help="Config modelu; bierzemy z niego serwer, sampling i przełącznik "
                             "rozumowania, żeby mierzyć to samo, co zmierzy pomiar")
    parser.add_argument("--temperatury", type=float, nargs="+", default=[0.6])
    parser.add_argument("--kary", type=float, nargs="+", default=[0.05, 0.15],
                        help="Wartości frequency_penalty")
    parser.add_argument("--pytania", type=int, default=16,
                        help="Ile pytań; rozdzielane po równo na 8 kategorii")
    parser.add_argument("--proby", type=int, default=2,
                        help="Ile razy każde pytanie; 16 pytań x 2 = 32 próby na wariant")
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args(argv)

    cfg = tomllib.load(args.config.open("rb"))
    cfg["_model"] = cfg["api"].get("model") or sonda.served_model(cfg["api"]["base_url"])[0]
    think = cfg.get("chat_template", {}).get("enable_thinking")
    baza = {k: v for k, v in cfg.get("generation", {}).items() if k != "frequency_penalty"}
    pytania = sonda.sample_questions(args.pytania)

    print(f"model:   {cfg['_model']}")
    print(f"serwer:  {cfg['api']['base_url']}")
    print(f"think:   {think}   max_tokens: {baza.get('max_tokens')}")
    warianty = [
        (f"t{t:.1f} fp{fp:.2f}".replace(".", ","), {**baza, "temperature": t,
                                                    "frequency_penalty": fp})
        for t, fp in itertools.product(args.temperatury, args.kary)
    ]
    zadania = [(n, gen, q) for n, gen in warianty for q in pytania
               for _ in range(args.proby)]
    start = time.time()
    with ThreadPoolExecutor(args.workers) as pula:
        wyniki = list(pula.map(lambda z: (z[0], rozmowa(cfg, z[1], z[2], think)), zadania))
    print(f"\n{len(zadania)} rozmów ({2 * len(zadania)} zapytań) w {time.time() - start:.0f}s\n")

    print(f"{'wariant':20} {'odp. tura1':>11} {'odp. tura2':>11} {'urwane':>9} "
          f"{'ślad':>7} {'odpow.':>7}")
    for nazwa, _ in warianty:
        grupa = [r for n, r in wyniki if n == nazwa]
        t1 = sum(1 for (_, _, o), _ in grupa if o)
        t2 = sum(1 for _, (_, _, o) in grupa if o)
        urwane = sum((a[0] == "length") + (b[0] == "length") for a, b in grupa)
        slady = [len(s) for para in grupa for _, s, _ in para if s]
        odp = [len(o) for para in grupa for _, _, o in para if o]
        print(f"{nazwa:20} {t1:>5}/{len(grupa):<5} {t2:>5}/{len(grupa):<5} "
              f"{urwane:>5}/{2 * len(grupa):<3} "
              f"{int(statistics.median(slady)) if slady else 0:>7} "
              f"{int(statistics.median(odp)) if odp else 0:>7}")
    print("\nMiara to mechanika, nie jakość - wybrany zestaw potwierdź ocenionym przebiegiem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
