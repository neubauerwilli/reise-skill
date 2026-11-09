---
name: reise-packliste
description: >-
  Der Packlisten-Bauer. Baut eine Packliste aus Ziel, Wetter, Dauer und Aktivitäten und
  nennt die Gepäckregeln der Airline. Nutze ihn, wenn der Nutzer sagt "was packe ich ein",
  "Packliste", "Koffer packen", "Handgepäck" oder "was brauche ich für die Reise".
argument-hint: "[Ziel] [von] [bis] [Aktivitäten]"
---

# reise-packliste

Weder zu viel noch zu wenig: Die Liste kommt aus dem Wetter am Ziel und dem, was du dort
vorhast.

## Grundregeln

Bucht nichts, gibt keine Zahlungsdaten ein. Wetterzahlen mit Quelle und Abrufzeit,
Gepäckregeln nur von der Seite der Airline und mit Abrufdatum, nie aus dem Gedächtnis.
Ergebnis nach `reise/packliste.md`.

## Schritt 1: fragen

Ziel, Reisedatum von bis, Aktivitäten (Strand, Wandern, Städtetrip, Skifahren, Tauchen,
Business), Airline und Tarif (nur Handgepäck?), Übernachtung (Hotel, Hostel, Zelt),
Waschmöglichkeit, Kinder, Medikamente, Geräte.

## Schritt 2: Wetter und Grundliste

```bash
python3 skills/reise-packliste/packliste.py Lissabon --von 2027-03-10 --bis 2027-03-17 --aktivitaeten strand,wandern
```

Das Werkzeug holt bei einer Reise in den nächsten 15 Tagen die Vorhersage, sonst das
Klimamittel des Vorjahres (Open-Meteo, kein Schlüssel) und baut daraus eine Liste mit
Wetter-Anpassung (Jacke, Regenzeug, Sonnenschutz) und Zusatz je Aktivität. Unter Windows
heißt der Aufruf oft `py`. Ohne Python: Leite die Liste selbst aus einer Wetterabfrage ab.

## Schritt 3: Gepäckregeln der Airline

Such per Websuche die Gepäckseite der gebuchten Airline und des Tarifs: Handgepäck
(Maße, Gewicht), Aufgabegepäck (Gewicht, Preis), Flüssigkeiten (100 ml im durchsichtigen
Beutel), Powerbanks (nur im Handgepäck, Grenzen je Airline). Nenne Quelle und Abrufdatum.
Gegen die Regel gepackt wird teuer am Schalter: sag es deutlich.

## Schritt 4: die Antwort

Abhaken-Liste nach Gruppen (Papiere, Technik, Gesundheit, Kleidung, Aktivität), Mengen
passend zur Dauer (ab einer Woche waschen, nicht mehr einpacken), eine Zeile je Posten,
dahinter die Gepäckgrenze und ein Satz, was du bei nur Handgepäck weglässt. Frag, was
fehlt oder zu viel ist.
