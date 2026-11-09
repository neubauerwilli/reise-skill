#!/usr/bin/env python3
"""Suchlinks für Flüge und Hotels bauen und gefundene Preise sauber vergleichen.

Kein Preisabruf, kein Konto, nichts wird gebucht. Zwei Befehle:

    python3 preise.py links --von BER --nach LIS --ab 2027-03-10 --bis 2027-03-17 --ort Lissabon --personen 2 --umkreis 150 --flexibel 3
    python3 preise.py tabelle angebote.json --haupt BER --min-bewertung 8.0

Die drei Spar-Hebel:
  --umkreis KM    Flughäfen im Umkreis des Abflughafens mit eigenen Suchlinks (Standard 150)
  --flexibel N    jedes Datum im Fenster plus minus N Tage, dazu Monatsansicht
  Hotels          Bewertung je 100 Euro (Preis-Leistung), Mindestbewertung, Booking-Filter

angebote.json: Liste mit art (flug|hotel), quelle, titel, preis (Euro, Gesamtpreis), link,
abgerufen (Datum und Uhrzeit). Flüge zusätzlich: flughafen, tag (JJJJ-MM-TT). Hotels:
bewertung (0 bis 10). Optional standard: true am Treffer, den man ohne Vergleich gebucht hätte.
Standardbibliothek, nur eingebaute Flughafentabelle.
"""
import argparse
import datetime as dt
import json
import math
import sys
import urllib.parse

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

# IATA: (Name, Breite, Länge). Deutschland, Österreich, Schweiz und nahe Nachbarn.
HAEFEN = {
    "BER": ("Berlin Brandenburg", 52.3667, 13.5033), "LEJ": ("Leipzig/Halle", 51.4324, 12.2416),
    "DRS": ("Dresden", 51.1328, 13.7672), "HAM": ("Hamburg", 53.6304, 9.9882),
    "BRE": ("Bremen", 53.0475, 8.7867), "HAJ": ("Hannover", 52.4611, 9.6851),
    "PAD": ("Paderborn/Lippstadt", 51.6141, 8.6163), "DTM": ("Dortmund", 51.5183, 7.6122),
    "DUS": ("Düsseldorf", 51.2895, 6.7668), "NRN": ("Weeze", 51.6024, 6.1422),
    "CGN": ("Köln/Bonn", 50.8659, 7.1427), "FRA": ("Frankfurt", 50.0379, 8.5622),
    "HHN": ("Frankfurt-Hahn", 49.9487, 7.2639), "SCN": ("Saarbrücken", 49.2146, 7.1095),
    "STR": ("Stuttgart", 48.6899, 9.2220), "FKB": ("Karlsruhe/Baden-Baden", 48.7794, 8.0805),
    "NUE": ("Nürnberg", 49.4987, 11.0669), "MUC": ("München", 48.3538, 11.7861),
    "FMM": ("Memmingen", 47.9888, 10.2395), "FDH": ("Friedrichshafen", 47.6713, 9.5115),
    "SZG": ("Salzburg", 47.7933, 13.0043), "INN": ("Innsbruck", 47.2602, 11.3440),
    "LNZ": ("Linz", 48.2332, 14.1875), "VIE": ("Wien", 48.1103, 16.5697),
    "GRZ": ("Graz", 46.9911, 15.4396), "KLU": ("Klagenfurt", 46.6425, 14.3377),
    "BTS": ("Bratislava", 48.1702, 17.2127), "ZRH": ("Zürich", 47.4647, 8.5492),
    "BSL": ("Basel", 47.5900, 7.5292), "GVA": ("Genf", 46.2381, 6.1089),
    "PRG": ("Prag", 50.1008, 14.2600), "WRO": ("Breslau", 51.1027, 16.8858),
    "AMS": ("Amsterdam", 52.3086, 4.7639), "CPH": ("Kopenhagen", 55.6180, 12.6508),
    "BRU": ("Brüssel", 50.9014, 4.4844), "LUX": ("Luxemburg", 49.6233, 6.2044),
}

q = urllib.parse.quote
WT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def km(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def umkreis(haupt, radius):
    if haupt not in HAEFEN:
        return [(haupt, haupt, 0)]
    h = HAEFEN[haupt]
    liste = [(c, v[0], km(h[1:], v[1:])) for c, v in HAEFEN.items() if km(h[1:], v[1:]) <= radius]
    return sorted(liste, key=lambda x: x[2])


def yymmdd(d):
    return d.strftime("%y%m%d")


def flug_links(von, nach, ab, bis, personen):
    g = "https://www.google.com/travel/flights?q=" + q(f"Flights from {von} to {nach} on {ab} through {bis}") + "&curr=EUR&hl=de"
    s = f"https://www.skyscanner.de/transport/fluge/{von.lower()}/{nach.lower()}/{yymmdd(ab)}/{yymmdd(bis)}/?adultsv2={personen}"
    return g, s


def links(a):
    ab, bis = dt.date.fromisoformat(a.ab), dt.date.fromisoformat(a.bis)
    dauer = bis - ab
    print("FLÜGE (öffnen und Preis ablesen, nichts wird gebucht)")
    haefen = umkreis(a.von.upper(), a.umkreis)
    if a.von.upper() not in HAEFEN:
        print(f"  Hinweis: {a.von.upper()} steht nicht in der eingebauten Tabelle, kein Umkreis. Nenne weitere Flughäfen selbst.")
    for code, name, d in haefen:
        tag = " (Hauptflughafen)" if code == a.von.upper() else f" ({d:.0f} km entfernt)"
        g, s = flug_links(code, a.nach.upper(), ab, bis, a.personen)
        print(f"\n  {code} {name}{tag}")
        print(f"    Google Flights: {g}")
        print(f"    Skyscanner:     {s}")
    if a.flexibel:
        print(f"\nFLEXIBEL: jedes Datum plus minus {a.flexibel} Tage (gleiche Reisedauer von {dauer.days} Tagen), ab {a.von.upper()}")
        for n in range(-a.flexibel, a.flexibel + 1):
            d1, d2 = ab + dt.timedelta(days=n), bis + dt.timedelta(days=n)
            g, s = flug_links(a.von.upper(), a.nach.upper(), d1, d2, a.personen)
            marke = " (dein Wunschtermin)" if n == 0 else ""
            print(f"  {d1:%d.%m.%Y} ({WT[d1.weekday()]}){marke}\n    Google: {g}\n    Sky:    {s}")
        mon = ab.strftime("%y%m")
        print(f"\n  Monatsansicht Skyscanner: https://www.skyscanner.de/transport/fluge/{a.von.lower()}/{a.nach.lower()}/?oym={mon}&iym={mon}&adultsv2={a.personen}")
        g, _ = flug_links(a.von.upper(), a.nach.upper(), ab, bis, a.personen)
        print(f"  Datumsgitter Google Flights: {g}")
        print("    (dort auf das Datumsfeld klicken, Reiter 'Datumsgitter' oder 'Preisdiagramm' wählen: zeigt den ganzen Monat)")
    if a.ort:
        print("\nHOTELS")
        basis = ("https://www.booking.com/searchresults.de.html?ss=" + q(a.ort) +
                 f"&checkin={a.ab}&checkout={a.bis}&group_adults={a.personen}&no_rooms=1&selected_currency=EUR")
        print(f"  Booking.com nach Preis:                {basis}&order=price")
        print(f"  Booking.com, Bewertung ab {a.min_bewertung:.1f}, nach Preis: {basis}&nflt=review_score%3D{int(a.min_bewertung * 10)}&order=price")
        print("  Google Hotels: https://www.google.com/travel/hotels/" + q(a.ort) + f"?q={q('Hotels in ' + a.ort)}")
    print(f"\nLinks gebaut am {dt.datetime.now():%d.%m.%Y %H:%M}. Preise ändern sich laufend: nach dem Ablesen immer mit Quelle und Uhrzeit festhalten.")


def wochentag(tag):
    try:
        d = dt.date.fromisoformat(tag)
        return f"{d:%d.%m.} ({WT[d.weekday()]})"
    except (TypeError, ValueError):
        return "-"


def tabelle(a):
    with open(a.datei, encoding="utf-8") as f:
        angebote = json.load(f)
    fluege = sorted([x for x in angebote if x.get("art") == "flug"], key=lambda x: x["preis"])
    hotels = [x for x in angebote if x.get("art") == "hotel"]
    jetzt_zeile = []

    if fluege:
        print("FLÜGE (günstigste zuerst)")
        bester = fluege[0]
        for x in fluege:
            marke = "   << günstigster" if x is bester else ""
            print(f"  {x['preis']:>6.0f} Euro  {wochentag(x.get('tag')):<12} {x.get('flughafen', '-'):<4} {x['titel']}{marke}")
            print(f"                 {x['quelle']}, abgerufen {x['abgerufen']}  {x['link']}")
        haupt = a.haupt.upper() if a.haupt else None
        if haupt:
            vom_haupt = sorted([x for x in fluege if x.get("flughafen", "").upper() == haupt], key=lambda x: x["preis"])
            print(f"\nPreis je Flughafen gegen {haupt}" + (f" (günstigster dort: {vom_haupt[0]['preis']:.0f} Euro)" if vom_haupt else ""))
            beste = {}
            for x in fluege:
                c = x.get("flughafen", "-").upper()
                beste.setdefault(c, x)
            for c, x in sorted(beste.items(), key=lambda kv: kv[1]["preis"]):
                if vom_haupt and c != haupt:
                    diff = vom_haupt[0]["preis"] - x["preis"]
                    zusatz = f"  ({'spart' if diff > 0 else 'kostet mehr'} {abs(diff):.0f} Euro gegen {haupt}; Anfahrt und Rückweg einrechnen)"
                else:
                    zusatz = ""
                print(f"  {c:<4} ab {x['preis']:.0f} Euro  am {wochentag(x.get('tag'))}{zusatz}")
        std = next((x for x in fluege if x.get("standard")), None)
        if std is None and haupt:
            std = next((x for x in fluege if x.get("flughafen", "").upper() == haupt), None)
        if std and bester["preis"] < std["preis"]:
            d = std["preis"] - bester["preis"]
            jetzt_zeile.append(f"FLUG: statt {std['preis']:.0f} Euro nur {bester['preis']:.0f} Euro (spart {d:.0f} Euro, {d / std['preis'] * 100:.0f} Prozent): "
                               f"{bester.get('flughafen', '-')} am {wochentag(bester.get('tag'))} statt {std.get('flughafen', '-')} am {wochentag(std.get('tag'))}")
        elif std is None:
            print("\nHinweis: Für die Ersparnis fehlt der Standardtreffer. Gib --haupt an oder markiere einen Flug mit \"standard\": true.")

    if hotels:
        mitbewertung = [x for x in hotels if x.get("bewertung") is not None]
        ohne = [x for x in hotels if x.get("bewertung") is None]
        gut = [x for x in mitbewertung if x["bewertung"] >= a.min_bewertung]
        schwach = [x for x in mitbewertung if x["bewertung"] < a.min_bewertung]
        wert = lambda x: x["bewertung"] / (x["preis"] / 100.0)
        gut.sort(key=wert, reverse=True)
        print(f"\nHOTELS nach Preis-Leistung (Bewertung je 100 Euro, Mindestbewertung {a.min_bewertung:.1f})")
        for i, x in enumerate(gut):
            marke = "   << bestes Preis-Leistungs-Verhältnis" if i == 0 else ""
            print(f"  {x['preis']:>6.0f} Euro  Bewertung {x['bewertung']:.1f}  Wert {wert(x):.2f}  {x['titel']}{marke}")
            print(f"                 {x['quelle']}, abgerufen {x['abgerufen']}  {x['link']}")
        for x in schwach:
            print(f"  ausgeschlossen (unter {a.min_bewertung:.1f}): {x['titel']}, {x['preis']:.0f} Euro, Bewertung {x['bewertung']:.1f}")
        for x in ohne:
            print(f"  ohne Bewertung (nicht gewertet): {x['titel']}, {x['preis']:.0f} Euro")
        std = next((x for x in hotels if x.get("standard")), None)
        if gut and std and std.get("bewertung") is not None:
            b = gut[0]
            if b["preis"] < std["preis"] and b["bewertung"] >= std["bewertung"] - 0.2:
                d = std["preis"] - b["preis"]
                jetzt_zeile.append(f"HOTEL: statt {std['preis']:.0f} Euro nur {b['preis']:.0f} Euro (spart {d:.0f} Euro, {d / std['preis'] * 100:.0f} Prozent) "
                                   f"bei Bewertung {b['bewertung']:.1f} statt {std['bewertung']:.1f}")

    if jetzt_zeile:
        print("\nERSPARNIS")
        for z in jetzt_zeile:
            print("  " + z)
    print("\nMomentaufnahme: Preise gelten nur zum genannten Abrufzeitpunkt und können beim Buchen abweichen. Gebucht wird nur von dir.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    l = sp.add_parser("links")
    l.add_argument("--von", required=True)
    l.add_argument("--nach", required=True)
    l.add_argument("--ab", required=True)
    l.add_argument("--bis", required=True)
    l.add_argument("--ort")
    l.add_argument("--personen", type=int, default=1)
    l.add_argument("--umkreis", type=int, default=150, help="Flughäfen im Umkreis in km (Standard 150, 0 = nur Hauptflughafen)")
    l.add_argument("--flexibel", type=int, default=0, help="plus minus N Tage um den Wunschtermin")
    l.add_argument("--min-bewertung", type=float, default=8.0)
    l.set_defaults(f=links)
    t = sp.add_parser("tabelle")
    t.add_argument("datei")
    t.add_argument("--haupt", help="Hauptflughafen (IATA) für den Vergleich")
    t.add_argument("--min-bewertung", type=float, default=8.0)
    t.set_defaults(f=tabelle)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
