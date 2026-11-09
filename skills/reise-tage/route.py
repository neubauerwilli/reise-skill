#!/usr/bin/env python3
"""Tagesrouten aus Orten bauen: Koordinaten (OpenStreetMap Nominatim), kurze Reihenfolge,
Wegzeiten zu Fuß und ein Google-Maps-Link je Tag. Kein API-Schlüssel.

Nominatim erlaubt höchstens eine Anfrage je Sekunde; das Skript wartet entsprechend.

    python3 route.py beispiel/tage.json
tage.json: {"stadt": "Lissabon", "tage": [{"titel": "Tag 1", "orte": ["Torre de Belém", "Pastéis de Belém"]}]}
"""
import argparse
import json
import math
import sys
import time
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

UA = "reise-skill/1.0 (https://github.com/neubauerwilli/reise-skill)"
_letzte = [0.0]


def geocode(name, stadt):
    warte = 1.1 - (time.time() - _letzte[0])
    if warte > 0:
        time.sleep(warte)
    url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" + urllib.parse.quote(f"{name}, {stadt}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        d = json.loads(r.read().decode("utf-8"))
    _letzte[0] = time.time()
    if not d:
        return None
    return float(d[0]["lat"]), float(d[0]["lon"]), d[0].get("display_name", name)


def km(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    dp = p2 - p1
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def reihenfolge(punkte):
    # Nächster-Nachbar ab dem ersten Ort. Für Tagesrouten mit fünf bis acht Orten reicht das.
    rest, weg = list(punkte[1:]), [punkte[0]]
    while rest:
        n = min(rest, key=lambda p: km(weg[-1]["pos"], p["pos"]))
        rest.remove(n)
        weg.append(n)
    return weg


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datei")
    ap.add_argument("--fest", action="store_true", help="Reihenfolge nicht ändern")
    a = ap.parse_args()
    with open(a.datei, encoding="utf-8") as f:
        plan = json.load(f)
    stadt = plan["stadt"]
    for tag in plan["tage"]:
        punkte, fehlt = [], []
        for o in tag["orte"]:
            g = geocode(o, stadt)
            if g:
                punkte.append({"name": o, "pos": (g[0], g[1])})
            else:
                fehlt.append(o)
        print(f"\n## {tag['titel']}")
        if not punkte:
            print("  keine Orte gefunden")
            continue
        weg = punkte if a.fest else reihenfolge(punkte)
        gesamt = 0.0
        for i, p in enumerate(weg):
            if i:
                d = km(weg[i - 1]["pos"], p["pos"]) * 1.3  # Umwegfaktor Luftlinie zu Fußweg
                gesamt += d
                print(f"     | etwa {d:.1f} km, zu Fuß rund {round(d / 4.5 * 60)} Minuten")
            print(f"  {i + 1}. {p['name']}  ({p['pos'][0]:.5f}, {p['pos'][1]:.5f})")
        ziel = weg[-1]["pos"]
        start = weg[0]["pos"]
        wp = "|".join(f"{p['pos'][0]},{p['pos'][1]}" for p in weg[1:-1])
        link = f"https://www.google.com/maps/dir/?api=1&origin={start[0]},{start[1]}&destination={ziel[0]},{ziel[1]}&travelmode=walking"
        if wp:
            link += "&waypoints=" + urllib.parse.quote(wp, safe=",")
        print(f"  Karte: {link}")
        print(f"  Fußweg gesamt grob {gesamt:.1f} km (Luftlinie mal 1,3, Näherung)")
        for o in fehlt:
            print(f"  nicht gefunden: {o} (Namen genauer schreiben)")
    print("\nÖffnungszeiten und Preise stehen nicht in Nominatim: vor dem Besuch auf der Seite des Ortes prüfen.")


if __name__ == "__main__":
    main()
