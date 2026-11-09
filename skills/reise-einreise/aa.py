#!/usr/bin/env python3
"""Reise- und Sicherheitshinweise des Auswärtigen Amts für ein Land (OpenData, kein Schlüssel).

Gibt Warnstufe, Stand-Datum und die Abschnitte zu Einreise, Visum, Impfungen aus dem Volltext.

    python3 aa.py Thailand
    python3 aa.py TH --abschnitt "Einreise" --abschnitt "Gesundheit"
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

UA = "reise-skill/1.0 (https://github.com/neubauerwilli/reise-skill)"


def hole(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def text(h):
    h = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", h or "")
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    return re.sub(r"\n\s*\n+", "\n", h).strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("land", help="Ländername (deutsch) oder ISO-Code")
    ap.add_argument("--abschnitt", action="append", default=None, help="Stichwort einer Überschrift, mehrfach möglich")
    ap.add_argument("--zeichen", type=int, default=1500, help="Höchstlänge je Abschnitt")
    a = ap.parse_args()
    stichworte = a.abschnitt or ["Einreise", "Zoll", "Impf", "Gesundheit"]

    uebersicht = hole("https://www.auswaertiges-amt.de/opendata/travelwarning")["response"]
    q = a.land.strip().lower()
    treffer = [(k, v) for k, v in uebersicht.items() if isinstance(v, dict) and
               (v.get("countryCode", "").lower() == q or v.get("iso3CountryCode", "").lower() == q or q in v.get("countryName", "").lower())]
    if not treffer:
        sys.exit(f"Kein Land '{a.land}' beim Auswärtigen Amt gefunden.")
    key, v = treffer[0]
    d = hole(f"https://www.auswaertiges-amt.de/opendata/travelwarning/{key}")["response"][key]
    jetzt = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    stand = dt.datetime.fromtimestamp(int(d["lastModified"])).strftime("%d.%m.%Y")
    print(f"{d['title']}")
    print(f"Quelle: Auswärtiges Amt OpenData, Hinweise zuletzt geändert {stand}, abgerufen {jetzt}")
    print(f"Reisewarnung: {'JA' if d.get('warning') else 'nein'}  Teilreisewarnung: {'JA' if d.get('partialWarning') else 'nein'}  "
          f"Sicherheitshinweis: {'JA' if d.get('situationWarning') else 'nein'}  für Teile: {'JA' if d.get('situationPartWarning') else 'nein'}")
    if d.get("lastChanges"):
        print("Letzte Änderungen:", text(d["lastChanges"])[:400].replace("\n", " "))
    html = d.get("content", "")
    teile = re.split(r"(?=<h[1-4][^>]*>)", html)
    gezeigt = 0
    for t in teile:
        m = re.match(r"<h[1-4][^>]*>(.*?)</h[1-4]>", t, re.S)
        if not m:
            continue
        titel = text(m.group(1))
        if any(s.lower() in titel.lower() for s in stichworte):
            print(f"\n## {titel}\n{text(t)[:a.zeichen]}")
            gezeigt += 1
    if not gezeigt:
        print("\nKeine Abschnitte zu den Stichworten gefunden. Anfang des Volltexts:\n" + text(html)[:a.zeichen])
    print(f"\nVolltext: https://www.auswaertiges-amt.de/opendata/travelwarning/{key}")
    print("Für Österreich: BMEIA reisewarnungen.at, für die Schweiz: EDA eda.admin.ch/reisehinweise (per Websuche prüfen).")


if __name__ == "__main__":
    main()
