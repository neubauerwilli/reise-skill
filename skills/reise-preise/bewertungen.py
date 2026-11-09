#!/usr/bin/env python3
"""Bewertungs-Check: zählt in Gästebewertungen, was wiederkehrt.

Claude liest die Bewertungen (Booking, Google, Tripadvisor) und schreibt sie in eine
JSON-Datei. Dieses Werkzeug zählt je Thema Lob und Kritik, zeigt wiederkehrende
Beschwerden mit Beispielsatz, prüft "sieht aus wie auf den Fotos" und rechnet
Preis-Leistung (Bewertung je 100 Euro, wie in preise.py). Kein Abruf, kein Konto.
Das Zählen ist eine Stichwortsuche in Deutsch und Englisch, keine Sprachanalyse:
Claude liest die Treffer gegen und urteilt.

    python3 bewertungen.py beispiel/bewertungen.json --min-bewertung 8.0

bewertungen.json: Liste von Hotels mit name, preis (Euro Gesamtpreis), bewertung (Durchschnitt),
quelle, abgerufen und reviews: [{"quelle": "...", "datum": "JJJJ-MM", "sterne": 1 bis 5 oder null, "text": "..."}]
"""
import argparse
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

# Thema: (Lob-Stichworte, Kritik-Stichworte)
THEMEN = {
    "Sauberkeit": (["sauber", "gepflegt", "clean", "spotless", "tidy"],
                   ["schmutzig", "dreckig", "verschmutzt", "staub", "haare", "fleck", "dirty", "filthy", "stain", "stained", "smelly", "stank"]),
    "Zustand": (["renoviert", "modern", "neu eingerichtet", "renovated", "well maintained", "new"],
                ["alt", "abgewohnt", "kaputt", "defekt", "schimmel", "renovierungsbedürftig", "tropft", "broken", "mold", "mould", "worn", "dated", "leak", "outdated", "rundown", "run-down"]),
    "Lage": (["zentral", "gute lage", "nah am", "nähe", "central", "great location", "close to", "walking distance"],
             ["abgelegen", "weit weg", "weit vom", "unsicher", "far from", "remote", "sketchy", "unsafe"]),
    "Lärm": (["ruhig", "leise", "quiet"],
             ["laut", "lärm", "baustelle", "noisy", "loud", "thin walls", "dünne wände"]),
    "Personal": (["freundlich", "hilfsbereit", "nett", "friendly", "helpful", "welcoming"],
                 ["unfreundlich", "unhöflich", "arrogant", "rude", "unhelpful", "dismissive"]),
    "Frühstück": (["frühstück war gut", "gutes frühstück", "tolles frühstück", "great breakfast", "good breakfast"],
                  ["frühstück schlecht", "mageres frühstück", "frühstück war mager", "poor breakfast", "bad breakfast"]),
    "Ungeziefer": ([], ["bettwanzen", "kakerlake", "kakerlaken", "ratte", "wanzen", "bed bugs", "bedbugs", "cockroach", "mice", "rat "]),
}
FOTOS_PASSEN = ["wie auf den fotos", "wie auf den bildern", "entspricht den fotos", "wie beschrieben", "as pictured", "as shown", "matches the photos", "just like the photos", "as described", "as in the photos"]
FOTOS_ANDERS = ["nicht wie auf den fotos", "anders als auf den fotos", "fotos täuschen", "bilder täuschen", "nicht wie beschrieben", "sieht anders aus", "weit besser auf den fotos", "photos are misleading", "not as pictured", "not as in the photos", "looks nothing like", "misleading photos", "doesn't look like the photos", "does not look like the photos", "smaller than it looks", "kleiner als auf den fotos", "fotos beschönigt", "photos are old", "outdated photos"]
SCHWER = {"Ungeziefer"}


def treffer(text, woerter):
    t = " " + text.lower() + " "
    out = []
    for w in woerter:
        if re.search(r"(?<![a-zäöüß])" + re.escape(w), t):
            out.append(w)
    return out


def satz(text, woerter):
    for s in re.split(r"(?<=[.!?])\s+", text):
        if treffer(s, woerter):
            return s.strip()
    return text[:120]


def verneint(text, w):
    # "nicht sauber", "not clean", "kein schimmel": ein einfaches Zeichen, dass das Lob oder die Kritik verneint ist
    t = text.lower()
    i = t.find(w)
    if i < 0:
        return False
    davor = t[max(0, i - 14):i]
    return bool(re.search(r"\b(nicht|kein|keine|keinen|not|no|never|wasn't|isn't)\b\s*(\w+\s*)?$", davor))


def pruefe(h):
    revs = h.get("reviews", [])
    n = len(revs)
    zaehl = {}
    for t, (lob, kritik) in THEMEN.items():
        pos, neg, neg_bsp, pos_bsp = 0, 0, None, None
        for r in revs:
            tx = r["text"]
            k = [w for w in treffer(tx, kritik) if not verneint(tx, w)]
            l = [w for w in treffer(tx, lob) if not verneint(tx, w)]
            kn = [w for w in treffer(tx, lob) if verneint(tx, w)]  # "nicht sauber" zählt als Kritik
            if k or kn:
                neg += 1
                neg_bsp = neg_bsp or satz(tx, kritik + lob)
            elif l:
                pos += 1
                pos_bsp = pos_bsp or satz(tx, lob)
        zaehl[t] = (pos, neg, pos_bsp, neg_bsp)
    passt = sum(1 for r in revs if treffer(r["text"], FOTOS_PASSEN) and not treffer(r["text"], FOTOS_ANDERS))
    anders = [r for r in revs if treffer(r["text"], FOTOS_ANDERS)]
    return n, zaehl, passt, anders


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("datei")
    ap.add_argument("--min-bewertung", type=float, default=8.0)
    ap.add_argument("--schwelle", type=float, default=0.2, help="Anteil der Bewertungen, ab dem eine Kritik als wiederkehrend gilt (Standard 0,2)")
    a = ap.parse_args()
    with open(a.datei, encoding="utf-8") as f:
        hotels = json.load(f)

    ergebnis = []
    for h in hotels:
        n, zaehl, passt, anders = pruefe(h)
        print(f"\n=== {h['name']}  |  {h['preis']:.0f} Euro, Durchschnitt {h['bewertung']:.1f}, {n} gelesene Bewertungen ({h.get('quelle', '?')}, abgerufen {h.get('abgerufen', '?')})")
        if n < 5:
            print(f"  Achtung: nur {n} Bewertungen gelesen. Zu wenig für ein Urteil, lies mehr.")
        warn = []
        for t, (pos, neg, pb, nb) in zaehl.items():
            if pos or neg:
                print(f"  {t:<11} Lob {pos}  Kritik {neg}")
        print("  Wiederkehrende Beschwerden:" if any(v[1] for v in zaehl.values()) else "  Keine Beschwerden gefunden.")
        for t, (pos, neg, pb, nb) in zaehl.items():
            if neg and (neg / max(n, 1) >= a.schwelle or t in SCHWER):
                tag = "SCHWER" if t in SCHWER else "wiederkehrend"
                print(f"    - {t}: {neg} von {n} ({neg / n * 100:.0f} Prozent), {tag}. Beispiel: \"{nb}\"")
                warn.append(t)
        print(f"  Sieht aus wie auf den Fotos: {passt} bestätigen, {len(anders)} widersprechen")
        for r in anders[:2]:
            print(f"    - \"{satz(r['text'], FOTOS_ANDERS)}\" ({r.get('quelle', '?')}, {r.get('datum', '?')})")
        wert = h["bewertung"] / (h["preis"] / 100.0)
        urteil = "empfehlen"
        if "Ungeziefer" in warn or len(anders) >= max(2, n * a.schwelle):
            urteil = "nicht empfehlen"
        elif len(warn) >= 2 or h["bewertung"] < a.min_bewertung:
            urteil = "mit Vorbehalt"
        ergebnis.append((urteil, wert, h, warn, anders))
        print(f"  Preis-Leistung: Bewertung {h['bewertung']:.1f} je 100 Euro = {wert:.2f}")
        print(f"  Urteil (Zählung, Claude liest gegen): {urteil}")

    print("\nRANGLISTE nach Preis-Leistung (nicht empfohlene unten)")
    rang = {"empfehlen": 0, "mit Vorbehalt": 1, "nicht empfehlen": 2}
    for u, w, h, warn, anders in sorted(ergebnis, key=lambda x: (rang[x[0]], -x[1])):
        zusatz = f", Kritik: {', '.join(warn)}" if warn else ""
        zusatz += ", Fotos widersprechen" if anders else ""
        print(f"  {u:<16} {h['name']}: {h['preis']:.0f} Euro, Bewertung {h['bewertung']:.1f}, Wert {w:.2f}{zusatz}")
    print("\nStichwortzählung, keine Sprachanalyse: Claude liest die Belege gegen, bevor ein Urteil dem Nutzer vorgelegt wird. Stand der Bewertungen: Abrufzeit oben.")


if __name__ == "__main__":
    main()
