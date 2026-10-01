#!/usr/bin/env python3
"""Wykresy postępu Poziomki na Łodydze wobec liczby tokenów SFT.

Źródłem liczb jest `leaderboard.md`, a nie katalogi przebiegów: tabela zawiera
już uzgodnione wyniki z trzech przebiegów i adnotacje o konfiguracji serwera.
Pozycję na osi X liczy `tokeny.toml` z batcha i tokenów na próbkę.

Porównujemy wyłącznie modele trenowane od zera przez polskie zespoły: Poziomkę,
Polankę i APT3 Instruct. Modele dostrajane z cudzej bazy (Bielik, Qra, polka)
to inna kategoria i tu nie wchodzą.

Co jest na wykresie:

* krzywa Poziomki - run2 i run4 sklejone w jeden ciągły trening, bo run4
  wystartował z wag run2 @ iter 1718 i widział wszystko, co run2;
* czerwona gwiazdka na końcu osi - merge, który powstaje ze złożenia wszystkich
  checkpointów, więc widział cały budżet tokenów;
* zielona i fioletowa gwiazdka w paśmie "nieznana" po lewej - Polanka i APT3,
  dla których nie znamy liczby tokenów SFT.

Dla każdego checkpointu bierzemy NAJLEPSZĄ konfigurację serwera i samplingu.
Ten sam checkpoint mierzyliśmy w oknie 8192 z RoPE 84000 i w 16384 z RoPE
640000, przy dwóch temperaturach; interesuje nas, co model potrafi w swoim
najlepszym ustawieniu, a nie średnia po konfiguracjach serwera.

Warianty rozumowania mają osobne wykresy, bo rozumowanie zmienia wynik
o kilkadziesiąt setnych i wspólny wykres mieszałby dwa różne zjawiska.

    python3 wykresy.py                  # 18 plików PNG do katalogu wykresy/
    python3 wykresy.py --tylko-ogolny   # sam wynik ogólny, bez kategorii
"""

import argparse
import re
import tomllib
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
LEADERBOARD = PROJECT_DIR / "leaderboard.md"
TOKENY = PROJECT_DIR / "tokeny.toml"
WYKRESY = PROJECT_DIR / "wykresy"

KATEGORIE = [
    ("pism", "piśmiennictwo"),
    ("role", "odgrywanie ról"),
    ("wnios", "wnioskowanie"),
    ("mat", "matematyka"),
    ("kod", "kodowanie"),
    ("ekstr", "ekstrakcja"),
    ("scisle", "nauki ścisłe"),
    ("human", "humanistyka"),
]

# Paleta zwalidowana dla jasnego tła #fcfcfb (validate_palette.js --pairs all:
# wszystkie testy zdane; zieleń i czerwień mają ΔE 7,2 przy protanopii, co jest
# dopuszczalne wyłącznie z drugim nośnikiem tożsamości - stąd podpis przy
# każdej gwiazdce, a nie sama legenda).
KRZYWA_KOLOR = "#2a78d6"
TLO = "#fcfcfb"
INK = "#1a1a19"
INK_SLABY = "#6b6b68"
SIATKA = "#e6e6e2"

# Pasmo "nieznana" po lewej stronie osi, we współrzędnych tokenów.
PASMO_SRODEK = -0.95
PASMO_ROZSTAW = 0.34
PASMO_GRANICA = -0.35


def liczba(text):
    """'1,65' -> 1.65; puste i '-' -> None."""
    text = text.strip().replace("**", "").replace("–", "-")
    if not text or text == "-":
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def czytaj_leaderboard(path=LEADERBOARD):
    """Wiersze tabeli jako słowniki. Ignoruje wszystko poza tabelą."""
    wiersze = []
    for line in path.read_text(encoding="utf-8").split("\n"):
        if not line.startswith("| ") or line.startswith("|---"):
            continue
        pola = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(pola) < 16 or pola[0] == "model":
            continue
        wynik = liczba(pola[4])
        if wynik is None:
            continue
        wiersz = {"etykieta": pola[0].strip("`"), "myslenie": pola[2], "wynik": wynik}
        for (klucz, _), surowe in zip(KATEGORIE, pola[8:16]):
            wiersz[klucz] = liczba(surowe)
        wiersze.append(wiersz)
    return wiersze


def baza_etykiety(etykieta):
    """'x (8k/84k, t0,8)' -> 'x'. Adnotacja konfiguracji nas tu nie interesuje."""
    m = re.match(r"^(.*?)\s*\([^)]*\)\s*$", etykieta)
    return m.group(1) if m else etykieta


def przelicznik_tokenow(config):
    """Mapa etykieta_przebiegu -> (seria, tokeny_na_krok, offset)."""
    przebiegi = {p["id"]: p for p in config["przebieg"]}
    out = {}
    for p in config["przebieg"]:
        offset = 0
        rodzic = p.get("start_przebieg")
        if rodzic:
            r = przebiegi[rodzic]
            offset = r["batch"] * r["tokeny_na_probke"] * p["start_krok"]
        out[p["etykieta"]] = (
            p.get("seria", ""),
            p["batch"] * p["tokeny_na_probke"],
            offset,
        )
    return out


def najlepszy(wiersze, myslenie, metryka, pasuje, pelna_etykieta=False):
    """Najwyższy wynik wśród wierszy, których baza spełnia `pasuje(baza)`.

    Tak realizujemy "najlepsza konfiguracja per checkpoint": ten sam checkpoint
    ma kilka wierszy (okno, RoPE, temperatura) i bierzemy z nich maksimum.
    `pelna_etykieta` wyłącza to dla przypadków, gdzie chcemy jedną wskazaną
    konfigurację, a nie najlepszą - wtedy dopasowujemy etykietę z adnotacją.
    """
    out = {}
    for w in wiersze:
        if w["myslenie"] not in myslenie or w.get(metryka) is None:
            continue
        baza = w["etykieta"] if pelna_etykieta else baza_etykiety(w["etykieta"])
        klucz = pasuje(baza)
        if klucz is None:
            continue
        if klucz not in out or w[metryka] > out[klucz][1]:
            out[klucz] = (baza, w[metryka])
    return out


def krzywa_poziomki(wiersze, config, myslenie, metryka):
    """[(tokeny_mld, wynik)] jednej ciągłej krzywej, posortowane po tokenach."""
    serie = przelicznik_tokenow(config)

    def pasuje(baza):
        m = re.match(r"^(.*?)/iter_0*(\d+)$", baza)
        if not m:
            return None
        przebieg, krok = m.group(1), int(m.group(2))
        if przebieg not in serie or not serie[przebieg][0]:
            return None
        return (przebieg, krok)

    punkty = []
    for (przebieg, krok), (_, wynik) in najlepszy(wiersze, myslenie, metryka, pasuje).items():
        _, na_krok, offset = serie[przebieg]
        punkty.append(((offset + na_krok * krok) / 1e9, wynik))
    return sorted(punkty)


def gwiazdki(wiersze, config, myslenie, metryka, x_merge):
    """[(x, wynik, opis, kolor)] - merge na końcu osi, reszta w paśmie."""
    out = []
    merge_cfg = config.get("merge", {})
    etykieta = merge_cfg.get("etykieta")
    if etykieta:
        # `konfiguracje` zawęża wybór do wskazanych ustawień serwera
        # i samplingu; w ich obrębie bierzemy najlepszy wynik dla metryki.
        kfg = merge_cfg.get("konfiguracje")
        cele = {f"{etykieta} ({k})" for k in kfg} if kfg else {etykieta}
        trafienia = najlepszy(
            wiersze, myslenie, metryka,
            lambda b, _c=cele: "merge" if b in _c else None,
            pelna_etykieta=bool(kfg),
        )
        if "merge" in trafienia:
            out.append((x_merge, trafienia["merge"][1],
                        merge_cfg.get("opis", "merge"),
                        merge_cfg.get("kolor", "#e34948")))

    nieznane = config.get("odniesienie", [])
    start = PASMO_SRODEK - PASMO_ROZSTAW * (len(nieznane) - 1) / 2
    for i, wpis in enumerate(nieznane):
        trafienia = najlepszy(
            wiersze, myslenie, metryka,
            lambda b, cel=wpis["etykieta"]: "x" if b == cel else None,
        )
        if "x" in trafienia:
            out.append((start + i * PASMO_ROZSTAW, trafienia["x"][1],
                        wpis.get("opis", wpis["etykieta"]), wpis.get("kolor", INK_SLABY)))
    return out


def rysuj(punkty, gwiazdy, tytul, podtytul, sciezka):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9.5, 5.6), dpi=140)
    fig.patch.set_facecolor(TLO)
    ax.set_facecolor(TLO)

    x = [p[0] for p in punkty]
    y = [p[1] for p in punkty]
    # Odcinek przez dużą dziurę w danych rysujemy przerywany. Między 3,9 a 7,9
    # mld tokenów nie zmierzyliśmy żadnego checkpointu run4, a ciągła linia
    # sugerowałaby tam przebieg, którego nie znamy.
    luka = max((x[i + 1] - x[i]) for i in range(len(x) - 1)) if len(x) > 1 else 0
    prog = max(1.5, (max(x) - min(x)) * 0.25)
    for i in range(len(x) - 1):
        przerwa = x[i + 1] - x[i] > prog
        ax.plot(x[i:i + 2], y[i:i + 2], color=KRZYWA_KOLOR, linewidth=2.0,
                linestyle=(0, (5, 3)) if przerwa else "-", zorder=3,
                alpha=0.55 if przerwa else 1.0)
    ax.plot(x, y, color=KRZYWA_KOLOR, linewidth=0, marker="o", markersize=6,
            markeredgecolor=TLO, markeredgewidth=1.5, label="Poziomka", zorder=4)
    if luka > prog:
        i = max(range(len(x) - 1), key=lambda j: x[j + 1] - x[j])
        ax.annotate("brak pomiarów", xy=((x[i] + x[i + 1]) / 2, (y[i] + y[i + 1]) / 2),
                    xytext=(0, -15), textcoords="offset points", ha="center",
                    fontsize=7.5, color=INK_SLABY, style="italic", zorder=5)
    ax.annotate("Poziomka", xy=(x[-1], y[-1]), xytext=(0, -16),
                textcoords="offset points", ha="center",
                fontsize=9, color=KRZYWA_KOLOR, fontweight="medium", zorder=5)

    for gx, gy, opis, kolor in gwiazdy:
        ax.plot([gx], [gy], marker="*", markersize=17, color=kolor,
                markeredgecolor=TLO, markeredgewidth=1.2, zorder=6,
                linestyle="none", label=opis)
        ax.annotate(f"{opis}\n{gy:.2f}".replace(".", ","), xy=(gx, gy),
                    xytext=(0, 13), textcoords="offset points", ha="center",
                    fontsize=8, color=kolor, fontweight="medium", zorder=6)

    wszystkie_y = y + [g[1] for g in gwiazdy]
    ax.set_ylim(0, max(wszystkie_y) * 1.35)
    ax.set_xlim(PASMO_SRODEK - PASMO_ROZSTAW - 0.3, max(x) + 0.75)

    # Granica pasma "nieznana": na lewo od niej pozycja na osi nic nie znaczy.
    ax.axvline(PASMO_GRANICA, color="#d8d8d4", linewidth=1.0,
               linestyle=(0, (3, 3)), zorder=1)
    ax.annotate("nieznana\nliczba tokenów", xy=(PASMO_SRODEK, 0),
                xytext=(0, -34), textcoords="offset points", ha="center",
                fontsize=8, color=INK_SLABY, annotation_clip=False)

    kroki = [t for t in (0, 2, 4, 6, 8, 10) if t <= max(x) + 0.5]
    ax.set_xticks(kroki)
    ax.set_xlabel("tokeny SFT (mld)", fontsize=9, color=INK_SLABY, labelpad=26)
    ax.set_ylabel("wynik Łodygi (0–10)", fontsize=9, color=INK_SLABY)
    ax.set_title(tytul, fontsize=12.5, color=INK, pad=16, loc="left",
                 fontweight="semibold")
    if podtytul:
        ax.text(0, 1.02, podtytul, transform=ax.transAxes, fontsize=8.5,
                color=INK_SLABY, va="bottom")

    ax.grid(True, axis="y", color=SIATKA, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for bok in ("top", "right"):
        ax.spines[bok].set_visible(False)
    for bok in ("left", "bottom"):
        ax.spines[bok].set_color("#d8d8d4")
    ax.tick_params(colors=INK_SLABY, labelsize=8.5)
    ax.legend(frameon=False, fontsize=8.5, labelcolor=INK_SLABY,
              loc="upper left", handletextpad=0.4)

    fig.subplots_adjust(left=0.085, right=0.975, top=0.86, bottom=0.2)
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(sciezka, facecolor=TLO)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tylko-ogolny", action="store_true")
    parser.add_argument("--wyjscie", type=Path, default=WYKRESY)
    args = parser.parse_args(argv)

    config = tomllib.loads(TOKENY.read_text(encoding="utf-8"))
    wiersze = czytaj_leaderboard()

    metryki = [("wynik", "wynik ogólny")]
    if not args.tylko_ogolny:
        metryki += KATEGORIE

    zapisane = 0
    for nazwa, dopuszczalne in [("nie", {"nie", "nie*", "brak"}), ("tak", {"tak"})]:
        for klucz, opis in metryki:
            punkty = krzywa_poziomki(wiersze, config, dopuszczalne, klucz)
            if not punkty:
                continue
            gwiazdy = gwiazdki(wiersze, config, dopuszczalne, klucz,
                               x_merge=max(p[0] for p in punkty))
            sciezka = args.wyjscie / f"{nazwa}-{klucz}.png"
            rysuj(
                punkty, gwiazdy,
                f"Poziomka: {opis} wobec tokenów SFT",
                ("bez rozumowania" if nazwa == "nie" else "z rozumowaniem")
                + " · najlepsza konfiguracja serwera i samplingu per checkpoint",
                sciezka,
            )
            zapisane += 1
    print(f"{zapisane} wykresów w {args.wyjscie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
