#!/usr/bin/env python3
"""Sonda: szybkie sprawdzenie modelu na API, zanim puścimy pełny pomiar.

Pełny przebieg to 3 × 160 tur i kilkanaście minut pracy sędziego. Sonda robi
kilkadziesiąt zapytań w kilkanaście sekund i odpowiada na pytania, które
przesądzają, czy pomiar w ogóle ma sens:

1. Czy model nie jest zepsuty? Zepsuty merge albo rozjazd wag z tokenizerem
   daje odpowiedzi złożone ze znaków zastępczych (U+FFFD), tabulatorów i
   znaków niedrukowalnych. Wykrywamy to przy `temperature = 0`, bo greedy nie
   ma losowości - jeśli tam wychodzą śmieci, to nie kwestia samplera.
   Tak odpadł poziomka-instruct-2026-09-30-2: 12/12 odpowiedzi to był szum,
   mediana 96-99% znaków-śmieci.

2. Czy szablon respektuje `enable_thinking`? Część serii ignoruje przełącznik
   i rozumuje mimo `false` - w 2026-09-21/iter_0000100 działo się to w 52% tur.
   Wtedy wariant "nothink" jest nazwą umowną i trzeba to odnotować w tabeli.

3. Jaki `max_tokens` się zmieści? Odczytujemy okno z /v1/models. Tura 2 liczy
   budżet podwójnie (prompt tury 2 zawiera odpowiedź z tury 1), więc
   max_tokens <= (okno - najdłuższa para pytań - szablon) / 2. Skrypt liczy to
   sam i domyślnie używa wyliczonej wartości.

4. Która temperatura pasuje? Mierzymy urwane, puste i zapętlone tury przy obu
   wartościach. Zalecenie nie przenosi się między modelami: 2026-09-24 i merge
   -1 zyskiwały na 0,8 bez rozumowania, a merge -3 tracił 0,20.

UWAGA na wielkość próbki. Domyślne 16 pytań wystarcza, by wyłapać zepsuty model
albo niedziałający przełącznik, ale NIE wystarcza do oceny zapętleń: sonda na
run4/iter_0000498 pokazała 0/16 zapętlonych, a pełny przebieg 13% z 480 tur.
Sonda odsiewa katastrofy i dobiera parametry; liczby do tabeli dają tylko
pełne przebiegi.

Użycie:
    python3 sonda.py                      # model z /v1/models, pełna sonda
    python3 sonda.py --tylko-smieci       # sam punkt 1, najszybszy
    python3 sonda.py --pytania 24 --max-tokens 3500
"""

import argparse
import json
import time
import unicodedata
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import runs

BASE_URL = "http://192.168.1.26:2300/v1"
# Zapas na narzut szablonu czatu w prompcie tury 2.
TEMPLATE_OVERHEAD = 40


def api(url, payload=None, timeout=600):
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def served_model(base_url):
    """Nazwa i okno kontekstu modelu wystawionego przez serwer."""
    entry = api(base_url.rstrip("/") + "/models")["data"][0]
    return entry["id"], int(entry.get("max_model_len") or 0)


def budget(window, questions):
    """Najwyższy max_tokens, przy którym KAŻDA tura mieści się w oknie.

    Prompt tury 2 to najdłuższa para pytań plus odpowiedź z tury 1, a potem
    dochodzi jeszcze generacja tury 2 - stąd dzielenie na dwa.
    """
    worst_chars = max(len(q["turns"][0]) + len(q["turns"][1]) for q in questions)
    worst_tokens = worst_chars // 3  # ~3 znaki na token dla polszczyzny
    return max(256, (window - worst_tokens - TEMPLATE_OVERHEAD) // 2)


def junk_ratio(text):
    """Udział znaków świadczących o rozjeżdżonym dekodowaniu tokenów.

    Pusta odpowiedź zwraca None, a NIE 1.0. Pustka i śmieci to dwie różne
    awarie: śmieci znaczą rozjazd wag z tokenizerem, a pustka zwykle to, że
    model rozumował i parser zabrał całą treść do `reasoning_content`. Zlanie
    ich w jedno dawało "MODEL ZEPSUTY" na zdrowym modelu, ktoremu nie dzialal
    przelacznik enable_thinking.
    """
    if not text.strip():
        return None
    bad = sum(
        1 for c in text
        if c == "�" or c in "\t\r" or unicodedata.category(c) in ("Co", "Cn")
    )
    return bad / len(text)


def max_repeat(text):
    """Ile razy powtarza się najczęstsza niepusta linia - miara zapętlenia."""
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 15]
    return Counter(lines).most_common(1)[0][1] if lines else 0


def sample_questions(count):
    """Po równo z każdej z 8 kategorii, tura 1."""
    by_category = {}
    for q in runs.read_jsonl(runs.QUESTIONS):
        by_category.setdefault(q["category"], []).append(q)
    per = max(1, count // len(by_category))
    return [q for group in by_category.values() for q in group[:per]]


def ask(base_url, model, question, think, temperature, max_tokens,
        frequency_penalty=0.05, top_p=0.9):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": question["turns"][0]}],
        "max_tokens": max_tokens,
        "stop": ["<|im_end|>"],
        "temperature": temperature,
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
    }
    if think is not None:
        payload["chat_template_kwargs"] = {"enable_thinking": think}
    result = api(base_url.rstrip("/") + "/chat/completions", payload)
    choice = result["choices"][0]
    message = choice["message"]
    reasoning = message.get("reasoning_content") or message.get("reasoning") or ""
    return {
        "finish": choice["finish_reason"],
        "answer": (message.get("content") or "").strip(),
        "reasoning": len(reasoning),
    }


def check_garbage(base_url, model, questions, workers):
    """Punkt 1: czy model w ogóle generuje tekst. Greedy plus jedna próba losowa."""
    print("== czy model nie jest zepsuty (0% śmieci = dobrze)")
    verdict = True
    for temperature in (0.0, 0.8):
        with ThreadPoolExecutor(workers) as pool:
            rows = list(pool.map(
                lambda q: ask(base_url, model, q, False, temperature, 400,
                              frequency_penalty=0.0),
                questions,
            ))
        ratios = sorted(r for r in (junk_ratio(x["answer"]) for x in rows)
                        if r is not None)
        puste = len(rows) - len(ratios)
        rozumuje = sum(1 for r in rows if r["reasoning"] > 0)
        if ratios:
            median = ratios[len(ratios) // 2]
            broken = sum(1 for r in ratios if r > 0.05)
            print(f"   temp={temperature}: mediana śmieci {median:.0%}, "
                  f"powyżej 5%: {broken}/{len(ratios)}, pustych {puste}/{len(rows)}"
                  + (f", rozumuje {rozumuje}" if rozumuje else ""))
            if broken > len(ratios) // 4:
                verdict = False
        else:
            print(f"   temp={temperature}: WSZYSTKIE odpowiedzi puste "
                  f"({puste}/{len(rows)}), rozumuje {rozumuje}")
            verdict = False
        tresc = next((x["answer"] for x in rows if x["answer"].strip()), "")
        print(f"      {tresc[:110]!r}")
        if puste and rozumuje >= puste:
            print(f"      UWAGA: przy enable_thinking=false {rozumuje} z {len(rows)} tur "
                  "rozumowało - to najpewniej przyczyna pustych odpowiedzi,")
            print("      a nie zepsute wagi. Sprawdź chat_template.jinja checkpointu.")
    if not verdict:
        print("\n   MODEL PODEJRZANY - nie mierz go, zanim nie sprawdzisz. Śmieci")
        print("   (U+FFFD, znaki sterujące) wskazują na rozjazd wag z tokenizerem:")
        print("   vocab_size w config.json, md5 tokenizer.json, rope_theta (także")
        print("   pod rope_parameters). Same puste odpowiedzi to zwykle szablon.")
    return verdict


def probe(base_url, model, questions, max_tokens, workers):
    """Punkty 2-4: oba tryby rozumowania, obie temperatury."""
    jobs = [(think, temperature, q)
            for think in (False, True)
            for temperature in (0.3, 0.8)
            for q in questions]
    started = time.time()
    with ThreadPoolExecutor(workers) as pool:
        rows = list(pool.map(
            lambda job: (job[:2], ask(base_url, model, job[2], job[0], job[1], max_tokens)),
            jobs,
        ))
    print(f"\n== sonda ({len(jobs)} zapytań w {time.time() - started:.0f}s, "
          f"max_tokens={max_tokens})")
    print(f"{'think':6} {'temp':>5} {'urwane':>8} {'puste':>6} {'zapętl':>8} "
          f"{'rozumuje':>9} {'śr.dł.':>7}")
    for key in [(False, 0.3), (False, 0.8), (True, 0.3), (True, 0.8)]:
        group = [r for k, r in rows if k == key]
        n = len(group)
        print(f"{str(key[0]):6} {key[1]:>5} "
              f"{sum(r['finish'] == 'length' for r in group):>4}/{n:<3} "
              f"{sum(not r['answer'] for r in group):>6} "
              f"{sum(max_repeat(r['answer']) > 5 for r in group):>4}/{n:<3} "
              f"{sum(r['reasoning'] > 0 for r in group):>5}/{n:<3} "
              f"{sum(len(r['answer']) for r in group) // n:>7}")
    off = [r for k, r in rows if k[0] is False and r["reasoning"] > 0]
    total_off = sum(1 for k, _ in rows if k[0] is False)
    if off:
        print(f"\n   UWAGA: przy enable_thinking=false {len(off)} z {total_off} tur "
              "i tak rozumowało.")
        print("   Szablon nie respektuje przełącznika - oznacz wiersz w tabeli.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--model", help="Domyślnie pierwszy wpis z /v1/models")
    parser.add_argument("--pytania", type=int, default=16,
                        help="Ile pytań w sondzie; rozdzielane po równo na 8 kategorii")
    parser.add_argument("--max-tokens", type=int,
                        help="Domyślnie wyliczone z okna kontekstu serwera")
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--tylko-smieci", action="store_true",
                        help="Tylko sprawdzenie, czy model nie jest zepsuty")
    args = parser.parse_args(argv)

    model, window = served_model(args.base_url)
    if args.model:
        model = args.model
    questions = sample_questions(args.pytania)
    max_tokens = args.max_tokens or budget(window, questions)
    print(f"model:  {model}")
    print(f"okno:   {window} -> max_tokens {max_tokens}\n")

    if not check_garbage(args.base_url, model, questions[:12], args.workers):
        return 1
    if not args.tylko_smieci:
        probe(args.base_url, model, questions, max_tokens, args.workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
