#!/usr/bin/env python3
"""Anspruch nach der EU-Fluggastrechte-Verordnung 261/2004 ausrechnen und Antrag schreiben.

Eingabe: Abflug, Ziel (IATA-Code oder Ortsname), Verspätung bei Ankunft, Grund.
Die Entfernung ist die Großkreis-Distanz zwischen den beiden Flughäfen (laut Verordnung
maßgeblich). Flughäfen: eingebaute Tabelle, sonst --von-koord / --nach-koord "lat,lon",
sonst Ortssuche über Open-Meteo (kein Schlüssel). Nur Standardbibliothek.

    python3 anspruch.py --von MUC --nach LIS --verspaetung 4 --grund technisch
    python3 anspruch.py --von FRA --nach JFK --art annullierung --vorwarnung-tage 3 --grund airline --antrag antrag.txt --name "Max Muster" --airline Lufthansa --flugnr LH400 --datum 2026-10-02
"""
import argparse
import json
import math
import sys
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

# IATA: (Name, Land, Breite, Länge)
FLUGHAEFEN = {
    "MUC": ("München", "DE", 48.3538, 11.7861), "FRA": ("Frankfurt", "DE", 50.0379, 8.5622),
    "BER": ("Berlin Brandenburg", "DE", 52.3667, 13.5033), "HAM": ("Hamburg", "DE", 53.6304, 9.9882),
    "DUS": ("Düsseldorf", "DE", 51.2895, 6.7668), "CGN": ("Köln/Bonn", "DE", 50.8659, 7.1427),
    "STR": ("Stuttgart", "DE", 48.6899, 9.2220), "NUE": ("Nürnberg", "DE", 49.4987, 11.0669),
    "LEJ": ("Leipzig/Halle", "DE", 51.4324, 12.2416), "HAJ": ("Hannover", "DE", 52.4611, 9.6851),
    "VIE": ("Wien", "AT", 48.1103, 16.5697), "SZG": ("Salzburg", "AT", 47.7933, 13.0043),
    "INN": ("Innsbruck", "AT", 47.2602, 11.3440), "GRZ": ("Graz", "AT", 46.9911, 15.4396),
    "ZRH": ("Zürich", "CH", 47.4647, 8.5492), "GVA": ("Genf", "CH", 46.2381, 6.1089),
    "BSL": ("Basel", "CH", 47.5900, 7.5292), "AMS": ("Amsterdam", "NL", 52.3086, 4.7639),
    "BRU": ("Brüssel", "BE", 50.9014, 4.4844), "CDG": ("Paris Charles de Gaulle", "FR", 49.0097, 2.5479),
    "ORY": ("Paris Orly", "FR", 48.7233, 2.3794), "LHR": ("London Heathrow", "GB", 51.4700, -0.4543),
    "LGW": ("London Gatwick", "GB", 51.1537, -0.1821), "STN": ("London Stansted", "GB", 51.8860, 0.2389),
    "DUB": ("Dublin", "IE", 53.4264, -6.2499), "MAD": ("Madrid", "ES", 40.4936, -3.5668),
    "BCN": ("Barcelona", "ES", 41.2974, 2.0833), "PMI": ("Palma de Mallorca", "ES", 39.5517, 2.7388),
    "IBZ": ("Ibiza", "ES", 38.8729, 1.3731), "AGP": ("Málaga", "ES", 36.6749, -4.4991),
    "TFS": ("Teneriffa Süd", "ES", 28.0445, -16.5725), "LPA": ("Gran Canaria", "ES", 27.9319, -15.3866),
    "LIS": ("Lissabon", "PT", 38.7742, -9.1342), "OPO": ("Porto", "PT", 41.2481, -8.6814),
    "FAO": ("Faro", "PT", 37.0144, -7.9659), "FCO": ("Rom Fiumicino", "IT", 41.8003, 12.2389),
    "MXP": ("Mailand Malpensa", "IT", 45.6306, 8.7281), "VCE": ("Venedig", "IT", 45.5053, 12.3519),
    "NAP": ("Neapel", "IT", 40.8860, 14.2908), "ATH": ("Athen", "GR", 37.9364, 23.9475),
    "HER": ("Heraklion", "GR", 35.3397, 25.1803), "IST": ("Istanbul", "TR", 41.2753, 28.7519),
    "AYT": ("Antalya", "TR", 36.8987, 30.8005), "CPH": ("Kopenhagen", "DK", 55.6180, 12.6508),
    "ARN": ("Stockholm Arlanda", "SE", 59.6519, 17.9186), "OSL": ("Oslo", "NO", 60.1976, 11.1004),
    "HEL": ("Helsinki", "FI", 60.3172, 24.9633), "WAW": ("Warschau", "PL", 52.1657, 20.9671),
    "PRG": ("Prag", "CZ", 50.1008, 14.2600), "BUD": ("Budapest", "HU", 47.4369, 19.2556),
    "ZAG": ("Zagreb", "HR", 45.7429, 16.0688), "SPU": ("Split", "HR", 43.5389, 16.2980),
    "DBV": ("Dubrovnik", "HR", 42.5614, 18.2682), "JFK": ("New York JFK", "US", 40.6413, -73.7781),
    "EWR": ("Newark", "US", 40.6895, -74.1745), "LAX": ("Los Angeles", "US", 33.9416, -118.4085),
    "MIA": ("Miami", "US", 25.7959, -80.2870), "ORD": ("Chicago O'Hare", "US", 41.9742, -87.9073),
    "YYZ": ("Toronto", "CA", 43.6777, -79.6248), "CUN": ("Cancún", "MX", 21.0365, -86.8771),
    "GRU": ("São Paulo", "BR", -23.4356, -46.4731), "DXB": ("Dubai", "AE", 25.2532, 55.3657),
    "DOH": ("Doha", "QA", 25.2731, 51.6081), "BKK": ("Bangkok", "TH", 13.6900, 100.7501),
    "SIN": ("Singapur", "SG", 1.3644, 103.9915), "HND": ("Tokio Haneda", "JP", 35.5494, 139.7798),
    "NRT": ("Tokio Narita", "JP", 35.7720, 140.3929), "DPS": ("Bali", "ID", -8.7482, 115.1675),
    "HKG": ("Hongkong", "HK", 22.3080, 113.9185), "DEL": ("Delhi", "IN", 28.5562, 77.1000),
    "CAI": ("Kairo", "EG", 30.1219, 31.4056), "HRG": ("Hurghada", "EG", 27.1783, 33.7994),
    "SSH": ("Scharm El-Scheich", "EG", 27.9773, 34.3950), "RAK": ("Marrakesch", "MA", 31.6069, -8.0363),
    "JNB": ("Johannesburg", "ZA", -26.1392, 28.2460), "CPT": ("Kapstadt", "ZA", -33.9715, 18.6021),
    "SYD": ("Sydney", "AU", -33.9399, 151.1753),
}

# EU plus Island, Norwegen und Schweiz: Abflug von dort fällt unter die Verordnung.
EU = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
      "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}
EWR_CH = EU | {"IS", "NO", "CH"}

# Gründe: (außergewöhnlich?, Erklärung)
GRUENDE = {
    "technisch": (False, "Technischer Defekt am Flugzeug: nach der Rechtsprechung in der Regel kein außergewöhnlicher Umstand, die Airline muss zahlen."),
    "airline": (False, "Grund liegt bei der Airline (Umlauf, Überbuchung, Planung): kein außergewöhnlicher Umstand."),
    "crew": (False, "Crew fehlt oder ist krank: liegt im Betrieb der Airline, kein außergewöhnlicher Umstand."),
    "streik-airline": (False, "Streik der eigenen Belegschaft der Airline: in der Regel kein außergewöhnlicher Umstand."),
    "unbekannt": (False, "Kein Grund genannt: Die Airline muss einen außergewöhnlichen Umstand beweisen, ohne Beleg gilt der Anspruch."),
    "wetter": (True, "Schlechtes Wetter, das den Flug unmöglich macht: außergewöhnlicher Umstand, meist kein Anspruch."),
    "flugsicherung": (True, "Flugsicherung (Streik, Sperrung des Luftraums): außergewöhnlicher Umstand, meist kein Anspruch."),
    "streik-flughafen": (True, "Streik von Flughafen- oder Sicherheitspersonal, das nicht zur Airline gehört: meist außergewöhnlich, kein Anspruch."),
    "sicherheit": (True, "Sicherheitsrisiko, Bombendrohung, Terror: außergewöhnlicher Umstand, meist kein Anspruch."),
    "vogelschlag": (True, "Vogelschlag oder Fremdkörper auf der Piste: meist außergewöhnlich, kein Anspruch."),
}


def de(n):
    return f"{n:,}".replace(",", ".")


def hole(url):
    req = urllib.request.Request(url, headers={"User-Agent": "reise-skill/1.0 (https://github.com/neubauerwilli/reise-skill)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def flughafen(eingabe, koord):
    if koord:
        lat, lon = [float(x) for x in koord.split(",")]
        return {"name": eingabe, "land": "?", "lat": lat, "lon": lon, "quelle": "Koordinaten von dir"}
    code = eingabe.strip().upper()
    if code in FLUGHAEFEN:
        n, land, lat, lon = FLUGHAEFEN[code]
        return {"name": f"{n} ({code})", "land": land, "lat": lat, "lon": lon, "quelle": "eingebaute Flughafentabelle"}
    d = hole("https://geocoding-api.open-meteo.com/v1/search?count=1&language=de&name=" + urllib.parse.quote(eingabe))
    if not d.get("results"):
        sys.exit(f"Ort '{eingabe}' nicht gefunden. Gib IATA-Code oder --von-koord/--nach-koord an.")
    r = d["results"][0]
    return {"name": f"{r['name']} (Ortsmitte, kein Flughafen)", "land": r.get("country_code", "?"),
            "lat": r["latitude"], "lon": r["longitude"], "quelle": "Open-Meteo Ortssuche (Näherung)"}


def grosskreis_km(a, b):
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dl = math.radians(b["lon"] - a["lon"])
    c = math.acos(max(-1.0, min(1.0, math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl))))
    return 6371.0 * c


def stufe(km, innerhalb_eu):
    if km <= 1500:
        return 250, "bis 1.500 km"
    if innerhalb_eu:
        return 400, "über 1.500 km innerhalb der EU"
    if km <= 3500:
        return 400, "1.500 bis 3.500 km"
    return 600, "über 3.500 km außerhalb der EU"


def pruefe(a):
    von, nach = flughafen(a.von, a.von_koord), flughafen(a.nach, a.nach_koord)
    km = grosskreis_km(von, nach)
    innerhalb = von["land"] in EWR_CH and nach["land"] in EWR_CH
    betrag, band = stufe(km, innerhalb)
    hinweise, gegen = [], []

    # 1. Gilt die Verordnung?
    if von["land"] in EWR_CH:
        gilt = True
    elif nach["land"] in EWR_CH and a.eu_airline == "ja":
        gilt = True
    elif nach["land"] in EWR_CH and a.eu_airline == "unklar":
        gilt = None
        hinweise.append("Abflug außerhalb der EU: Die Verordnung gilt nur, wenn die Airline ihren Sitz in der EU hat. Gib --eu-airline ja oder nein an.")
    else:
        gilt = False
    if "GB" in (von["land"], nach["land"]) and gilt is not True:
        hinweise.append("Großbritannien hat seit dem Brexit eine eigene Regel (UK261, gleiche Stufen in Pfund). Dort prüfen.")
    if gilt is False:
        gegen.append("Die Verordnung gilt für diesen Flug nicht (Abflug außerhalb der EU auf einer Airline von außerhalb der EU).")

    # 2. Grund
    ausser, gtext = GRUENDE[a.grund]
    if ausser:
        gegen.append(gtext)
    else:
        hinweise.append(gtext)

    # 3. Art des Falls
    if a.art == "verspaetung":
        if a.verspaetung < 3:
            gegen.append(f"Verspätung bei Ankunft {a.verspaetung:g} Stunden: Der Anspruch beginnt ab 3 Stunden am Zielort.")
        elif betrag == 600 and a.verspaetung < 4:
            betrag = 300
            hinweise.append("Über 3.500 km und weniger als 4 Stunden Verspätung: Die Airline darf auf die Hälfte kürzen (300 Euro).")
    elif a.art == "annullierung":
        t = a.vorwarnung_tage
        if t is None:
            hinweise.append("Wann wurde die Annullierung mitgeteilt? Gib --vorwarnung-tage an, ab 14 Tagen vorher gibt es keinen Ausgleich.")
        elif t >= 14:
            gegen.append("Annullierung mindestens 14 Tage vor Abflug mitgeteilt: kein Ausgleich.")
        elif t >= 7 and a.ersatzflug and a.frueher <= 2 and a.verspaetung < 4:
            gegen.append("Annullierung 7 bis 13 Tage vorher mit Ersatzflug (höchstens 2 Stunden früher, unter 4 Stunden später am Ziel): kein Ausgleich.")
        elif t < 7 and a.ersatzflug and a.frueher <= 1 and a.verspaetung < 2:
            gegen.append("Annullierung unter 7 Tage vorher, aber Ersatzflug höchstens 1 Stunde früher und unter 2 Stunden später am Ziel: kein Ausgleich.")
        if not gegen and betrag == 600 and a.ersatzflug and 0 < a.verspaetung < 4:
            betrag = 300
            hinweise.append("Ersatzflug kommt weniger als 4 Stunden später an: Kürzung auf die Hälfte (300 Euro) möglich.")
    else:
        hinweise.append("Nichtbeförderung gegen deinen Willen (zum Beispiel Überbuchung): gleiche Beträge. Wer freiwillig verzichtet, hat meist keinen Anspruch.")

    if gegen:
        anspruch = False
    elif gilt is None or (a.art == "annullierung" and a.vorwarnung_tage is None):
        anspruch = None
    else:
        anspruch = True

    return {"von": von, "nach": nach, "km": round(km), "betrag": betrag, "band": band, "innerhalb_eu": innerhalb,
            "gilt": gilt, "anspruch": anspruch, "gegen": gegen, "hinweise": hinweise}


def antrag(a, e):
    art = {"verspaetung": "erheblichen Verspätung bei der Ankunft", "annullierung": "Annullierung",
           "nichtbefoerderung": "Nichtbeförderung"}[a.art]
    if a.art == "verspaetung":
        grund = f"Mein Flug kam am Zielort mit rund {a.verspaetung:g} Stunden Verspätung an."
    elif a.art == "annullierung":
        grund = "Mein Flug wurde annulliert."
        if a.vorwarnung_tage is not None:
            grund += f" Ich wurde {a.vorwarnung_tage} Tage vor dem Abflug informiert."
    else:
        grund = "Mir wurde trotz gültiger Buchung und rechtzeitigem Erscheinen die Beförderung verweigert."
    betrag = e["betrag"]
    return f"""Betreff: Ausgleichszahlung nach Verordnung (EG) Nr. 261/2004, Flug {a.flugnr or '[Flugnummer]'} am {a.datum or '[Datum]'}

An {a.airline or '[Airline]'}
Kundenservice, Fluggastrechte

Sehr geehrte Damen und Herren,

am {a.datum or '[Datum]'} sollte ich mit Flug {a.flugnr or '[Flugnummer]'} von {e['von']['name']} nach {e['nach']['name']} fliegen (Buchungsnummer {a.buchung or '[Buchungsnummer]'}).

Der Flug war von einer {art} betroffen. {grund} Die Entfernung zwischen den Flughäfen beträgt rund {de(e['km'])} km (Großkreis-Distanz).

Nach Artikel 7 der Verordnung (EG) Nr. 261/2004 steht mir deshalb eine Ausgleichszahlung von {betrag} Euro zu. Einen außergewöhnlichen Umstand im Sinne von Artikel 5 Absatz 3 haben Sie mir nicht nachgewiesen. Sollten Sie sich darauf berufen, bitte ich um einen konkreten Nachweis.

Bitte überweisen Sie {betrag} Euro bis zum {a.frist or '[Datum, in 14 Tagen]'} auf folgendes Konto:
Kontoinhaber: {a.name or '[Name]'}
IBAN: [deine IBAN, trage sie selbst ein]

Zusätzlich bitte ich um Erstattung der Kosten für Verpflegung, Unterkunft und Transfer, die durch die Störung entstanden sind (Belege liegen bei, falls vorhanden).

Ohne Zahlung bis zu diesem Datum schalte ich die zuständige Schlichtungsstelle oder Durchsetzungsstelle ein.

Mit freundlichen Grüßen
{a.name or '[Name]'}
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--von", required=True)
    ap.add_argument("--nach", required=True)
    ap.add_argument("--von-koord")
    ap.add_argument("--nach-koord")
    ap.add_argument("--art", choices=["verspaetung", "annullierung", "nichtbefoerderung"], default="verspaetung")
    ap.add_argument("--verspaetung", type=float, default=0.0, help="Stunden Verspätung bei Ankunft am Ziel (bei Annullierung: des Ersatzflugs)")
    ap.add_argument("--grund", choices=sorted(GRUENDE), default="unbekannt")
    ap.add_argument("--eu-airline", choices=["ja", "nein", "unklar"], default="unklar")
    ap.add_argument("--vorwarnung-tage", type=int)
    ap.add_argument("--ersatzflug", action="store_true", help="Die Airline hat dir einen Ersatzflug angeboten")
    ap.add_argument("--frueher", type=float, default=0.0, help="Stunden, die der Ersatzflug früher abfliegt")
    ap.add_argument("--airline")
    ap.add_argument("--flugnr")
    ap.add_argument("--datum")
    ap.add_argument("--buchung")
    ap.add_argument("--name")
    ap.add_argument("--frist")
    ap.add_argument("--antrag", help="Antragstext in diese Datei schreiben")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    e = pruefe(a)
    if a.json:
        print(json.dumps(e, ensure_ascii=False, indent=2))
    else:
        print(f"Strecke: {e['von']['name']} nach {e['nach']['name']}")
        print(f"Entfernung (Großkreis): {de(e['km'])} km  [{e['von']['quelle']} / {e['nach']['quelle']}]")
        print(f"Stufe: {e['band']}, {e['betrag']} Euro je Fluggast")
        print("Verordnung gilt:", {True: "ja", False: "nein", None: "unklar"}[e["gilt"]])
        v = {True: f"ANSPRUCH, {e['betrag']} Euro je Fluggast", False: "KEIN Anspruch auf Ausgleich nach diesen Angaben",
             None: "UNKLAR, Angaben fehlen"}[e["anspruch"]]
        print("Ergebnis:", v)
        for g in e["gegen"]:
            print("  dagegen:", g)
        for h in e["hinweise"]:
            print("  Hinweis:", h)
        print("Rechenstufen nach Verordnung (EG) 261/2004; Grenzfälle vor dem Absenden prüfen. Keine Rechtsberatung.")
    if a.antrag:
        if e["anspruch"] is not True:
            print("Antrag nicht geschrieben: Anspruch nicht bestätigt. Prüfe die Angaben oben.")
        else:
            with open(a.antrag, "w", encoding="utf-8") as f:
                f.write(antrag(a, e))
            print("Antrag geschrieben:", a.antrag, "(abschicken tust du selbst)")


if __name__ == "__main__":
    main()
