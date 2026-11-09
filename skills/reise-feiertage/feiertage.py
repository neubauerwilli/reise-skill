#!/usr/bin/env python3
"""Feiertage im Reisezeitraum. Quelle: Nager.Date (kein Schlüssel).

    python3 feiertage.py --land PT --von 2027-04-01 --bis 2027-04-14
Land als ISO-Code (PT, TH, US, ...). Nager.Date deckt nicht jedes Land ab.
"""
import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--land", required=True)
    ap.add_argument("--von", required=True)
    ap.add_argument("--bis", required=True)
    a = ap.parse_args()
    von, bis = dt.date.fromisoformat(a.von), dt.date.fromisoformat(a.bis)
    gefunden = []
    for j in range(von.year, bis.year + 1):
        url = f"https://date.nager.at/api/v3/PublicHolidays/{j}/{a.land.upper()}"
        req = urllib.request.Request(url, headers={"User-Agent": "reise-skill/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                gefunden += json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            sys.exit(f"Nager.Date kennt {a.land.upper()} für {j} nicht (HTTP {e.code}). Per Websuche prüfen.")
    print(f"Feiertage {a.land.upper()} von {a.von} bis {a.bis} (Quelle Nager.Date, abgerufen {dt.datetime.now():%d.%m.%Y %H:%M}):")
    n = 0
    for h in gefunden:
        d = dt.date.fromisoformat(h["date"])
        if von <= d <= bis:
            n += 1
            wo = "landesweit" if h.get("global") else "nur in Regionen " + ", ".join(h.get("counties") or [])
            print(f"  {d:%d.%m.%Y} ({d.strftime('%a')})  {h['localName']} / {h['name']}  [{wo}]")
    if not n:
        print("  keine gesetzlichen Feiertage im Zeitraum")
    print("Nicht enthalten: religiöse Festzeiten ohne Feiertag, Messen, Konzerte, Schulferien. Dafür per Websuche nachsehen.")


if __name__ == "__main__":
    main()
