#!/usr/bin/env python3
"""Klima und Sicherheitslage für ein Reiseziel, aus freien Quellen ohne Schlüssel.

Klima: Open-Meteo (Archiv, Mittel über mehrere Vorjahre für den Reisemonat).
Sicherheitslage: Auswärtiges Amt OpenData (Reise- und Sicherheitshinweise).
Nur Standardbibliothek.

    python3 ziel.py Lissabon --monat 3
    python3 ziel.py "Bali" --monat 7 --jahre 3
"""
import argparse
import calendar
import datetime as dt
import json
import re
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


def ort(name, land=None):
    url = "https://geocoding-api.open-meteo.com/v1/search?count=1&language=de&name=" + urllib.parse.quote(name)
    if land:
        url += "&countryCode=" + land.upper()
    d = hole(url)
    if not d.get("results"):
        sys.exit(f"Ort '{name}' nicht gefunden.")
    return d["results"][0]


def klima(lat, lon, monat, jahre):
    heute = dt.date.today()
    letztes = heute.year - 1
    temps_max, temps_min, regen, regentage = [], [], [], []
    for j in range(letztes - jahre + 1, letztes + 1):
        ende = calendar.monthrange(j, monat)[1]
        d = hole("https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s&start_date=%d-%02d-01&end_date=%d-%02d-%02d"
                 "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto" % (lat, lon, j, monat, j, monat, ende))
        t = d["daily"]
        temps_max += [x for x in t["temperature_2m_max"] if x is not None]
        temps_min += [x for x in t["temperature_2m_min"] if x is not None]
        r = [x for x in t["precipitation_sum"] if x is not None]
        regen.append(sum(r))
        regentage.append(sum(1 for x in r if x >= 1.0))
    n = max(1, jahre)
    return {"tmax": sum(temps_max) / len(temps_max), "tmin": sum(temps_min) / len(temps_min),
            "regen_mm": sum(regen) / n, "regentage": sum(regentage) / n,
            "jahre": f"{letztes - jahre + 1} bis {letztes}"}


def html_text(h):
    h = re.sub(r"<br\s*/?>|</p>|</li>|</h\d>", "\n", h or "")
    h = re.sub(r"<[^>]+>", "", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\n\s*\n+", "\n", h).strip()


def sicherheit(code):
    uebersicht = hole("https://www.auswaertiges-amt.de/opendata/travelwarning")["response"]
    for k, v in uebersicht.items():
        if isinstance(v, dict) and v.get("countryCode") == code:
            return k, v
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ziel")
    ap.add_argument("--monat", type=int, required=True, help="Reisemonat 1 bis 12")
    ap.add_argument("--land", help="ISO-Code, wenn der Ortsname mehrdeutig ist (Bali ist sonst in Indien)")
    ap.add_argument("--jahre", type=int, default=3, help="Wie viele Vorjahre für das Klimamittel")
    a = ap.parse_args()

    o = ort(a.ziel, a.land)
    print(f"Ziel: {o['name']}, {o.get('country', '?')} ({o.get('country_code', '?')})  Koordinaten {o['latitude']:.2f}, {o['longitude']:.2f}")
    k = klima(o["latitude"], o["longitude"], a.monat, a.jahre)
    print(f"Klima im {a.monat}. Monat (Mittel {k['jahre']}, Quelle Open-Meteo Archiv):")
    print(f"  Tageshöchstwert {k['tmax']:.0f} Grad, Tiefstwert {k['tmin']:.0f} Grad, Regen {k['regen_mm']:.0f} mm an {k['regentage']:.0f} Tagen")

    key, s = sicherheit(o.get("country_code", ""))
    jetzt = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    if not s:
        print(f"Sicherheitslage: Kein Eintrag des Auswärtigen Amts für {o.get('country_code')} gefunden. Abgerufen {jetzt}.")
        return
    stand = dt.datetime.fromtimestamp(int(s["lastModified"])).strftime("%d.%m.%Y")
    flags = []
    if s.get("warning"):
        flags.append("REISEWARNUNG")
    if s.get("partialWarning"):
        flags.append("Teilreisewarnung")
    if s.get("situationWarning"):
        flags.append("Sicherheitshinweis zur Lage")
    if s.get("situationPartWarning"):
        flags.append("Sicherheitshinweis für Teile des Landes")
    print(f"Sicherheitslage (Auswärtiges Amt, Hinweise zuletzt geändert {stand}, abgerufen {jetzt}):")
    print("  " + (", ".join(flags) if flags else "keine Warnung markiert") + f"  |  {s['title']}")
    print(f"  Volltext: https://www.auswaertiges-amt.de/opendata/travelwarning/{key}")


if __name__ == "__main__":
    main()
