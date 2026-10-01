#!/usr/bin/env python3
"""Tabela porównawcza jako PNG: wybrany merge Poziomki wobec Polanki i APT3.

To nie jest wykres, tylko liczby złożone w obraz - do wklejenia tam, gdzie
tabela markdownowa się nie wyświetli. Dane bierzemy z `leaderboard.md`, żeby
nie powstała druga, rozjeżdżająca się kopia wyników.

Porównujemy wyłącznie modele trenowane od zera przez polskie zespoły. Każdy
wariant rozumowania dostaje własną, najlepszą dla siebie konfigurację serwera
i samplera - bo optimum wychodzi gdzie indziej dla trybu z rozumowaniem
i bez niego. Wewnątrz wariantu konfiguracja jest JEDNA dla wszystkich
kategorii: inaczej kolumna pokazywałaby liczby, których nie da się uzyskać
z jednego uruchomienia. Użyte ustawienia wypisuje stopka obrazka.

    python3 tabela.py
"""

import argparse
import re
from pathlib import Path

from wykresy import KATEGORIE, NA_PROCENT, czytaj_leaderboard, INK, INK_SLABY, SIATKA, TLO

PROJECT_DIR = Path(__file__).resolve().parent
WYJSCIE = PROJECT_DIR / "wykresy" / "porownanie.png"

# (nagłówek kolumny, etykieta w leaderboardzie, wariant rozumowania)
KOLUMNY = [
    ("bez rozum.", "poziomka-instruct-2026-09-30-7", {"nie"}),
    ("z rozum.", "poziomka-instruct-2026-09-30-7", {"tak"}),
    ("bez rozum.", "polanka-3.7B-exp", {"brak", "nie"}),
    ("z rozum.", "polanka-3.7B-exp", {"tak"}),
    ("bez rozum.", "APT3-1B-Instruct-v1", {"brak", "nie"}),
    ("z rozum.", "APT3-1B-Instruct-v1", {"tak"}),
]
GRUPY = [
    ("Poziomka\nwybrany merge", 0, 2, "#2a78d6"),
    ("Polanka 3.7B", 2, 2, "#008300"),
    ("APT3 Instruct 1B", 4, 2, "#4a3aa7"),
]
ZRODLA = [
    "Poziomka: merge checkpointów SFT (poziomka-instruct-2026-09-30-7)",
    "Polanka: piotr-ai/polanka_3.7b_exp_wip_260901",
    "APT3 Instruct: Azurro/APT3-1B-Instruct-v1",
]


def wybierz_konfiguracje(wiersze):
    """Dla każdej kolumny: pełna etykieta wiersza o najwyższym wyniku ogólnym.

    Kategorie bierzemy potem WYŁĄCZNIE z tej jednej konfiguracji, a nie
    z maksimum per kategoria - inaczej kolumna byłaby zlepkiem kilku
    uruchomień serwera i nie odpowiadałaby żadnemu realnemu ustawieniu.
    """
    wybrane = []
    for _, etykieta, warianty in KOLUMNY:
        najlepszy = None
        for w in wiersze:
            baza = re.sub(r"\s*\([^)]*\)\s*$", "", w["etykieta"])
            if baza != etykieta and w["etykieta"] != etykieta:
                continue
            if w["myslenie"] not in warianty:
                continue
            if najlepszy is None or w["wynik"] > najlepszy["wynik"]:
                najlepszy = w
        wybrane.append(najlepszy)
    return wybrane


def zbierz(wiersze):
    """([(metryka, [wartości])], [wybrane wiersze]) - kolumny to KOLUMNY."""
    wybrane = wybierz_konfiguracje(wiersze)
    metryki = [("wynik", "wynik ogólny")] + KATEGORIE
    tabela = [(opis, [None if w is None else w.get(klucz) for w in wybrane])
              for klucz, opis in metryki]
    return tabela, wybrane


def rysuj(tabela, wybrane, sciezka):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    wiersze_n = len(tabela)
    fig_h = 2.15 + 0.34 * wiersze_n + 0.17 * (len(ZRODLA) + 1)
    fig, ax = plt.subplots(figsize=(9.4, fig_h), dpi=150)
    fig.patch.set_facecolor(TLO)
    ax.set_facecolor(TLO)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    x_metryka = 0.015
    x_start, szer = 0.30, 0.1165
    gora = 0.985

    ax.text(x_metryka, gora, "Poziomka wobec polskich modeli trenowanych od zera",
            fontsize=13, color=INK, fontweight="semibold", va="top")
    ax.text(x_metryka, gora - 0.062,
            "wynik Łodygi jako % maksimum rubryki · 3 przebiegi · jeden zestaw "
            "samplera na tryb rozumowania",
            fontsize=8, color=INK_SLABY, va="top")

    y_grupy = gora - 0.135
    for nazwa, od, ile, kolor in GRUPY:
        srodek = x_start + szer * (od + ile / 2)
        ax.text(srodek, y_grupy, nazwa, fontsize=9.5, color=kolor,
                ha="center", va="top", fontweight="bold", linespacing=1.35)
        ax.plot([x_start + szer * od + 0.008, x_start + szer * (od + ile) - 0.008],
                [y_grupy - 0.072, y_grupy - 0.072],
                color=kolor, linewidth=1.6, alpha=0.75)

    y_naglowek = y_grupy - 0.105
    for i, (podpis, _, _) in enumerate(KOLUMNY):
        ax.text(x_start + szer * (i + 0.5), y_naglowek, podpis, fontsize=7.5,
                color=INK_SLABY, ha="center", va="top")

    # Wysokość wiersza liczona z miejsca, które ZOSTAJE po nagłówkach i stopce.
    # Wpisana na sztywno rozjeżdżała się i stopka wypadała poza obraz.
    y = y_naglowek - 0.052
    stopka = 0.030 * (len(ZRODLA) + 1) + 0.030
    wys = max(0.03, (y - stopka) / wiersze_n)
    for nr, (opis, wartosci) in enumerate(tabela):
        glowny = (nr == 0)
        if glowny:
            ax.add_patch(plt.Rectangle((x_metryka - 0.008, y - wys * 0.82),
                                       1 - 2 * (x_metryka - 0.008), wys * 0.95,
                                       facecolor="#f1f1ed", edgecolor="none", zorder=0))
        ax.text(x_metryka, y - wys * 0.22, opis, fontsize=9 if glowny else 8.5,
                color=INK if glowny else INK_SLABY, va="center",
                fontweight="semibold" if glowny else "normal")
        obecne = [v for v in wartosci if v is not None]
        najlepsza = max(obecne) if obecne else None
        for i, v in enumerate(wartosci):
            if v is None:
                tekst, kolor, waga = "—", "#b8b8b2", "normal"
            else:
                tekst = f"{v * NA_PROCENT:.1f}".replace(".", ",")
                czolo = (v == najlepsza)
                kolor = INK if czolo else INK_SLABY
                waga = "bold" if czolo else "normal"
            ax.text(x_start + szer * (i + 0.5), y - wys * 0.22, tekst,
                    fontsize=9.5 if glowny else 9, color=kolor,
                    ha="center", va="center", fontweight=waga)
        if not glowny:
            ax.plot([x_metryka - 0.008, 1 - x_metryka + 0.008],
                    [y - wys * 0.82, y - wys * 0.82],
                    color=SIATKA, linewidth=0.7, zorder=0)
        y -= wys

    y -= 0.022
    uzyte = []
    for (podpis, _, _), w in zip(KOLUMNY, wybrane):
        if w is None:
            continue
        m = re.search(r"\(([^)]*)\)\s*$", w["etykieta"])
        uzyte.append(f"{podpis.replace('rozum.', 'rozumowania')}: "
                     + (m.group(1) if m else "ustawienia domyślne"))
    if uzyte:
        ax.text(x_metryka, y, "Poziomka · " + " · ".join(uzyte[:2]),
                fontsize=7, color=INK_SLABY, va="top")
        y -= 0.036
    for zrodlo in ZRODLA:
        ax.text(x_metryka, y, zrodlo, fontsize=7, color=INK_SLABY, va="top")
        y -= 0.036

    fig.subplots_adjust(left=0.004, right=0.996, top=0.995, bottom=0.005)
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(sciezka, facecolor=TLO)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wyjscie", type=Path, default=WYJSCIE)
    args = parser.parse_args(argv)
    tabela, wybrane = zbierz(czytaj_leaderboard())
    rysuj(tabela, wybrane, args.wyjscie)
    print(f"zapisano {args.wyjscie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
