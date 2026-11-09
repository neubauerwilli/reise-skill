#!/usr/bin/env python3
"""Packliste aus Wetter, Dauer und Aktivitäten. Wetter: Open-Meteo (kein Schlüssel).

Liegt die Reise in den nächsten 15 Tagen, kommt die Vorhersage; sonst das Klimamittel
des Vorjahres für denselben Zeitraum.

    python3 packliste.py Lissabon --von 2027-03-10 --bis 2027-03-17 --aktivitaeten strand,wandern
"""
import argparse
import datetime as dt
import json
import sys
import urllib.parse
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


ZUSATZ = {
    "strand": ["Badesachen", "Strandtuch", "Sonnenbrille", "Sandalen"],
    "wandern": ["Wanderschuhe", "Tagesrucksack", "Trinkflasche", "Blasenpflaster"],
    "staedtetrip": ["bequeme Schuhe", "kleine Umhängetasche", "Powerbank"],
    "skifahren": ["Skibrille", "Handschuhe", "Skiunterwäsche", "Skipass"],
    "tauchen": ["Tauchzertifikat", "Maske", "Reef-sichere Sonnencreme"],
    "business": ["Hemd oder Bluse", "Laptop samt Ladegerät", "Visitenkarten"],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ziel")
    ap.add_argument("--von", required=True)
    ap.add_argument("--bis", required=True)
    ap.add_argument("--aktivitaeten", default="")
    a = ap.parse_args()
    von, bis = dt.date.fromisoformat(a.von), dt.date.fromisoformat(a.bis)
    tage = (bis - von).days + 1
    g = hole("https://geocoding-api.open-meteo.com/v1/search?count=1&language=de&name=" + urllib.parse.quote(a.ziel))
    if not g.get("results"):
        sys.exit("Ort nicht gefunden.")
    o = g["results"][0]
    heute = dt.date.today()
    if von <= heute + dt.timedelta(days=14) and von >= heute:
        quelle = "Vorhersage"
        d = hole(f"https://api.open-meteo.com/v1/forecast?latitude={o['latitude']}&longitude={o['longitude']}&start_date={a.von}&end_date={a.bis}"
                 "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,uv_index_max&timezone=auto")
    else:
        quelle = "Klimamittel des Vorjahres"
        yr = heute.year - 1
        v0 = von.replace(year=yr)
        v1 = bis.replace(year=yr + (bis.year - von.year))
        d = hole(f"https://archive-api.open-meteo.com/v1/archive?latitude={o['latitude']}&longitude={o['longitude']}&start_date={v0}&end_date={v1}"
                 "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto")
    t = d["daily"]
    ok = lambda xs: [x for x in xs if x is not None]
    tmax, tmin, regen = ok(t["temperature_2m_max"]), ok(t["temperature_2m_min"]), ok(t["precipitation_sum"])
    mx, mn = sum(tmax) / len(tmax), sum(tmin) / len(tmin)
    rt = sum(1 for x in regen if x >= 1.0)
    print(f"{o['name']}, {o.get('country', '')}: {a.von} bis {a.bis}, {tage} Tage ({quelle}, Open-Meteo, abgerufen {dt.datetime.now():%d.%m.%Y %H:%M})")
    print(f"Tagsüber {mx:.0f} Grad, nachts {mn:.0f} Grad, Regen an {rt} von {len(regen)} Tagen")

    liste = {"Papiere und Geld": ["Pass oder Ausweis (Gültigkeit prüfen)", "Bankkarte und etwas Bargeld", "Reiseversicherung, Buchungsbestätigungen"],
             "Technik": ["Handy und Ladegerät", "Reiseadapter, falls Steckdosen abweichen"],
             "Gesundheit": ["persönliche Medikamente", "Sonnencreme"],
             "Kleidung": []}
    wechsel = min(tage, 7)
    liste["Kleidung"] += [f"{wechsel + 1} Unterwäsche und Socken", f"{max(2, wechsel // 2)} Hosen oder Röcke", f"{wechsel} Oberteile"]
    if mx >= 25:
        liste["Kleidung"] += ["Shorts, leichte Kleidung", "Sonnenhut"]
    if mx < 15 or mn < 7:
        liste["Kleidung"] += ["warme Jacke", "Pullover"]
    elif mx < 22:
        liste["Kleidung"] += ["leichte Jacke oder Strickjacke"]
    if rt >= max(2, len(regen) // 4):
        liste["Kleidung"] += ["Regenjacke oder kleiner Schirm", "wasserfeste Schuhe"]
    for akt in [x.strip().lower() for x in a.aktivitaeten.split(",") if x.strip()]:
        liste.setdefault("Für " + akt, []).extend(ZUSATZ.get(akt, [f"Ausrüstung für {akt} (selbst ergänzen)"]))
    for k, v in liste.items():
        print(f"\n{k}")
        for x in v:
            print(f"  [ ] {x}")
    print("\nGepäckregeln deiner Airline (Handgepäck, Aufgabegepäck, Flüssigkeiten) stehen auf deren Seite: per Websuche holen und hier ergänzen.")


if __name__ == "__main__":
    main()
