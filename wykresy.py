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

Powstają dwa pliki: `wykresy/nie.png` i `wykresy/tak.png`. Każdy to siatka 3x3
- wynik ogólny plus osiem kategorii - we wspólnej skali, żeby dało się je
porównywać między sobą.

    python3 wykresy.py
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
# Kolory nagłówka wariantu: niebieski jak krzywa dla trybu bez rozumowania,
# pomarańczowy dla trybu z rozumowaniem. Oba ze zwalidowanej palety.
WARIANT_KOLOR = {"nie": "#2a78d6", "tak": "#eb6834"}
TLO = "#fcfcfb"
INK = "#1a1a19"
INK_SLABY = "#6b6b68"
SIATKA = "#e6e6e2"

# Łodyga punktuje w skali 0-10, ale na wykresie pokazujemy procent maksimum:
# przy wynikach rzędu 1,5/10 oś procentowa czyta się łatwiej niż ułamki, bo
# "15%" od razu mówi, jak daleko modelowi do pułapu.
NA_PROCENT = 10.0

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


def panel(ax, punkty, gwiazdy, tytul, x_zakres, y_max, pokaz_os_y):
    """Jeden wykres w siatce. Wszystkie dzielą skalę, żeby dało się je porównać."""
    x = [p[0] for p in punkty]
    y = [p[1] * NA_PROCENT for p in punkty]
    # Odcinek przez dużą dziurę w danych rysujemy przerywany - ciągła linia
    # sugerowałaby przebieg, którego nie zmierzyliśmy.
    prog = max(1.5, (x_zakres[1] - x_zakres[0]) * 0.25)
    for i in range(len(x) - 1):
        przerwa = x[i + 1] - x[i] > prog
        ax.plot(x[i:i + 2], y[i:i + 2], color=KRZYWA_KOLOR, linewidth=1.6,
                linestyle=(0, (4, 3)) if przerwa else "-",
                alpha=0.5 if przerwa else 1.0, zorder=3)
    ax.plot(x, y, color=KRZYWA_KOLOR, linewidth=0, marker="o", markersize=4,
            markeredgecolor=TLO, markeredgewidth=1.0, label="Poziomka", zorder=4)
    # Wartość przy każdym checkpoincie. Bez tego odczytanie, czy dołek to 9%
    # czy 11%, wymagałoby mierzenia wzrokiem po siatce.
    for i, (px, py) in enumerate(zip(x, y)):
        # Podpis ZAWSZE nad punktem - jednolity kierunek czyta się szybciej niż
        # etykiety skaczące nad i pod krzywą. Ostatni checkpoint leży pod
        # gwiazdką merge'u, więc jego podpis odsuwamy w lewo, wciąż u góry.
        w_lewo = (i == len(x) - 1)
        ax.annotate(f"{py:.0f}", xy=(px, py),
                    xytext=(-11 if w_lewo else 0, 7),
                    textcoords="offset points",
                    ha="right" if w_lewo else "center",
                    fontsize=6, color=INK_SLABY, zorder=5)

    # Gwiazdki w paśmie stoją blisko siebie w poziomie, a bywa, że i w pionie
    # (kodowanie: 5% i 2%). Podpis zawsze idzie nad markerem; przy kolizji
    # z już postawionym wędruje wyżej, nigdy pod spód.
    postawione = []
    for gx, gy_surowe, opis, kolor in gwiazdy:
        gy = gy_surowe * NA_PROCENT
        ax.plot([gx], [gy], marker="*", markersize=13, color=kolor,
                markeredgecolor=TLO, markeredgewidth=0.9, linestyle="none",
                label=opis, zorder=6)
        # Wartość przy gwiazdce: paleta ma zieleń i czerwień blisko siebie przy
        # protanopii, więc identyfikacja nie może opierać się na samym kolorze.
        for dy in (9, 20, 31):
            y_etykiety = gy + dy * (y_max / 320)
            if not any(abs(gx - px) < 0.75 and abs(y_etykiety - py) < y_max * 0.13
                       for px, py in postawione):
                break
        postawione.append((gx, y_etykiety))
        ax.annotate(f"{gy:.0f}", xy=(gx, gy),
                    xytext=(0, dy), textcoords="offset points",
                    ha="center", fontsize=6.5, color=kolor, zorder=6)

    ax.set_title(tytul, fontsize=9.5, color=INK, pad=6, loc="left")
    ax.set_xlim(*x_zakres)
    ax.set_ylim(0, y_max)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}")
    ax.axvline(PASMO_GRANICA, color="#d8d8d4", linewidth=0.8,
               linestyle=(0, (3, 3)), zorder=1)
    ax.grid(True, axis="y", color=SIATKA, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for bok in ("top", "right"):
        ax.spines[bok].set_visible(False)
    for bok in ("left", "bottom"):
        ax.spines[bok].set_color("#d8d8d4")
    ax.tick_params(colors=INK_SLABY, labelsize=7)
    if not pokaz_os_y:
        ax.tick_params(labelleft=False)


def rysuj_siatke(panele, tytul, naglowek, naglowek_kolor, podtytul, sciezka):
    """Jeden PNG: wynik ogólny jako wyróżniony panel plus osiem kategorii.

    Wynik ogólny dostaje własny, szerszy box u góry z jasnym tłem i ramką, bo
    jest liczbą, którą się cytuje; kategorie to rozbicie, które się czyta po
    nim. W równej siatce 3x3 ginął wśród ośmiu paneli o tej samej wadze.

    Wszystkie panele dzielą oś X i Y. Wspólna skala jest tu ważniejsza niż
    rozdzielczość pojedynczej kategorii: bez niej kodowanie (0,0-0,8) wyglądałoby
    jak piśmiennictwo (0,8-2,9) i nie dałoby się zobaczyć, że to zupełnie różne
    poziomy.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x_wszystkie = [p[0] for _, punkty, _ in panele for p in punkty]
    x_zakres = (PASMO_SRODEK - PASMO_ROZSTAW - 0.3, max(x_wszystkie) + 0.6)

    def gorny_poziom(punkty, gwiazdy):
        """Sufit osi Y dla jednego panelu, z zapasem na podpisy.

        Skala jest WŁASNA dla każdej kategorii, nie wspólna: kodowanie kończy
        się na 5%, a piśmiennictwo na 26%, więc wspólna oś zostawiałaby
        w połowie paneli wielkie puste pole. Ceną jest to, że wysokości słupków
        między panelami nie da się porównywać wzrokiem - dlatego podziałka
        procentowa jest widoczna w KAŻDYM panelu, a nie tylko w lewej kolumnie.
        """
        wartosci = ([p[1] for p in punkty] + [g[1] for g in gwiazdy]) or [0.1]
        return max(wartosci) * NA_PROCENT * 1.28
    kroki = [t for t in (0, 2, 4, 6, 8) if t <= max(x_wszystkie) + 0.5]

    fig = plt.figure(figsize=(10.5, 9.0), dpi=135)
    fig.patch.set_facecolor(TLO)
    siatka = fig.add_gridspec(4, 3, height_ratios=[1.3, 1, 1, 1],
                              hspace=0.34, wspace=0.17,
                              left=0.055, right=0.99, top=0.868, bottom=0.085)

    glowny = fig.add_subplot(siatka[0, :])
    glowny.set_facecolor("#f4f4f1")
    for bok in ("top", "right", "left", "bottom"):
        glowny.spines[bok].set_visible(True)
        glowny.spines[bok].set_color("#cfcfc9")
    panel(glowny, panele[0][1], panele[0][2], panele[0][0], x_zakres,
          gorny_poziom(panele[0][1], panele[0][2]), pokaz_os_y=True)
    glowny.set_title(panele[0][0], fontsize=11.5, color=INK, pad=8, loc="left",
                     fontweight="semibold")
    glowny.set_xticks(kroki)

    osie = [glowny]
    for i, (opis, punkty, gwiazdy) in enumerate(panele[1:]):
        ax = fig.add_subplot(siatka[1 + i // 3, i % 3])
        ax.set_facecolor(TLO)
        panel(ax, punkty, gwiazdy, opis, x_zakres, gorny_poziom(punkty, gwiazdy),
              pokaz_os_y=True)
        # Podziałka tokenów w KAŻDYM panelu: przy siatce odczytanie pozycji
        # dołka z górnego rzędu wymagałoby inaczej wodzenia wzrokiem niżej.
        ax.set_xticks(kroki)
        osie.append(ax)

    fig.suptitle(tytul, fontsize=13, color=INK, x=0.012, y=0.991,
                 ha="left", fontweight="semibold")
    fig.text(0.012, 0.955, naglowek, fontsize=15, color=naglowek_kolor,
             ha="left", va="top", fontweight="bold")
    fig.text(0.012, 0.922, podtytul, fontsize=8.5, color=INK_SLABY,
             ha="left", va="top")
    fig.text(0.5, 0.014, "tokeny SFT (miliardy) · na lewo od linii przerywanej "
             "pasmo modeli o nieznanej liczbie tokenów SFT",
             fontsize=8.5, color=INK_SLABY, ha="center")
    fig.text(0.002, 0.5, "wynik Łodygi (% maksimum rubryki)", fontsize=9, color=INK_SLABY,
             va="center", rotation="vertical")

    uchwyty, etykiety = glowny.get_legend_handles_labels()
    fig.legend(uchwyty, etykiety, frameon=False, fontsize=8.5, labelcolor=INK_SLABY,
               ncol=len(etykiety), loc="lower center", bbox_to_anchor=(0.5, 0.032))

    sciezka.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(sciezka, facecolor=TLO)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wyjscie", type=Path, default=WYKRESY)
    args = parser.parse_args(argv)

    config = tomllib.loads(TOKENY.read_text(encoding="utf-8"))
    wiersze = czytaj_leaderboard()

    metryki = [("wynik", "wynik ogólny")] + KATEGORIE
    for nazwa, dopuszczalne in [("nie", {"nie", "nie*", "brak"}), ("tak", {"tak"})]:
        panele = []
        for klucz, opis in metryki:
            punkty = krzywa_poziomki(wiersze, config, dopuszczalne, klucz)
            if not punkty:
                continue
            gwiazdy = gwiazdki(wiersze, config, dopuszczalne, klucz,
                               x_merge=max(p[0] for p in punkty))
            panele.append((opis, punkty, gwiazdy))
        if not panele:
            continue
        sciezka = args.wyjscie / f"{nazwa}.png"
        rysuj_siatke(
            panele,
            "Poziomka wobec tokenów SFT",
            "wyłączone rozumowanie" if nazwa == "nie" else "włączone rozumowanie",
            WARIANT_KOLOR[nazwa],
            "najlepsza konfiguracja serwera i samplingu per checkpoint",
            sciezka,
        )
        print(f"zapisano {sciezka}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
