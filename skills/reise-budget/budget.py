#!/usr/bin/env python3
"""Reisekosten in Euro und Landeswährung, Tageslimit. Kurse: Frankfurter (EZB), kein Schlüssel.

    python3 budget.py --waehrung THB --tage 10 --flug 780 --hotel-nacht 65 --essen-tag 25 --transfer 90 --budget 2000
Alle Beträge in Euro. Optional --extras 150 für Eintritte und Sonstiges.
"""
import argparse
import json
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def kurs(waehrung):
    if waehrung.upper() == "EUR":
        return 1.0, "EUR", "kein Kurs nötig"
    url = f"https://api.frankfurter.dev/v1/latest?base=EUR&symbols={waehrung.upper()}"
    req = urllib.request.Request(url, headers={"User-Agent": "reise-skill/1.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    return d["rates"][waehrung.upper()], d["date"], "api.frankfurter.dev (EZB-Referenzkurs)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--waehrung", required=True, help="Landeswährung, z. B. THB, USD, TRY")
    ap.add_argument("--tage", type=int, required=True)
    ap.add_argument("--flug", type=float, default=0.0)
    ap.add_argument("--hotel-nacht", type=float, default=0.0)
    ap.add_argument("--essen-tag", type=float, default=0.0)
    ap.add_argument("--transfer", type=float, default=0.0)
    ap.add_argument("--extras", type=float, default=0.0)
    ap.add_argument("--budget", type=float)
    a = ap.parse_args()

    k, datum, quelle = kurs(a.waehrung)
    naechte = max(0, a.tage - 1)
    posten = [("Flug", a.flug), (f"Hotel ({naechte} Nächte)", a.hotel_nacht * naechte),
              (f"Essen ({a.tage} Tage)", a.essen_tag * a.tage), ("Transfers", a.transfer), ("Sonstiges", a.extras)]
    summe = sum(p[1] for p in posten)
    print(f"Kurs: 1 EUR = {k} {a.waehrung.upper()}  (Stand {datum}, {quelle})")
    print(f"{'Posten':<24}{'Euro':>10}{a.waehrung.upper():>14}")
    for n, v in posten:
        print(f"{n:<24}{v:>10.0f}{v * k:>14.0f}")
    print(f"{'Summe':<24}{summe:>10.0f}{summe * k:>14.0f}")
    if a.budget is not None:
        rest = a.budget - a.flug - a.hotel_nacht * naechte - a.transfer - a.extras
        print(f"Budget {a.budget:.0f} Euro: übrig für Essen und Alltag {rest:.0f} Euro, Tageslimit {rest / a.tage:.0f} Euro "
              f"({rest / a.tage * k:.0f} {a.waehrung.upper()}) pro Tag." if rest >= 0 else
              f"Budget {a.budget:.0f} Euro reicht nicht: es fehlen {-rest:.0f} Euro schon vor dem Essen.")
    print("Momentaufnahme: Kurse und Preise schwanken, vor der Reise neu rechnen.")


if __name__ == "__main__":
    main()
