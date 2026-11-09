---
name: reise-ziel
description: >-
  Der Ziel-Finder. Fragt Budget, Reisezeit, Abflughafen und Interessen und schlägt drei bis
  fünf Reiseziele vor, je mit Wetter zur Reisezeit, grober Kostenspanne mit Quelle und
  Sicherheitslage. Nutze ihn, wenn der Nutzer sagt "wohin soll ich reisen", "Urlaubsziel",
  "wo ist es im März warm", "Reiseidee", "wohin mit 1.500 Euro" oder "Urlaub planen".
argument-hint: "[Budget] [Reisemonat] [Abflughafen]"
---

# reise-ziel

Die erste Frage jeder Reise: wohin. Dieser Skill macht daraus drei bis fünf echte
Vorschläge mit Zahlen.

## Grundregeln

Bucht nie, schickt nichts ab, gibt keine Zahlungsdaten ein. Jeder Preis kommt mit Quelle
und Abrufzeit und gilt als Momentaufnahme. Sicherheits- und Einreiseangaben nie aus dem
Gedächtnis, immer mit Abrufdatum. Es werden keine Bilder, Videos oder Töne erzeugt.
Ergebnis nach `reise/ziele.md` im Projektordner des Nutzers.

## Schritt 1: fragen

Frag in einem Rutsch: Gesamtbudget pro Person (oder pro Reise), Reisemonat und Dauer,
Abflughafen, Was soll die Reise bringen (Strand, Stadt, Natur, Essen, Abenteuer, Ruhe),
Wer fährt mit (allein, Paar, Familie, Kinder), Ausschlüsse (Hitze, lange Flüge, Visum).
Fehlt etwas, schlag eine Annahme vor und kennzeichne sie.

## Schritt 2: Kandidaten sammeln

Nenn zehn mögliche Ziele im Kopf, such dann per Websuche nach Reisezielen für die Zeit und
die Interessen und prüf, ob der Flug in die Budgetspanne passt. Wirf Ziele raus, die nicht
passen, und sag kurz warum.

## Schritt 3: pro Ziel Zahlen holen

Für jedes der drei bis fünf Ziele:

```bash
python3 skills/reise-ziel/ziel.py "Lissabon" --monat 3
python3 skills/reise-ziel/ziel.py "Bali" --land ID --monat 7
```

Das Werkzeug holt das Klimamittel der letzten drei Jahre für den Reisemonat (Open-Meteo,
kein Schlüssel) und die Reise- und Sicherheitshinweise des Auswärtigen Amts (OpenData,
mit Stand-Datum). Gib `--land` an, wenn der Ortsname mehrdeutig ist. Unter Windows heißt der
Aufruf oft `py`.

Dazu per Websuche: grobe Kosten für Flug (aus dem Abflughafen), Hotel pro Nacht und Essen,
jeweils mit Quelle und Abrufzeit. Bei den Kosten sagen: Spanne, Momentaufnahme. Genaue Preise
macht `/reise-preise`.

## Schritt 4: die Antwort

Für jedes Ziel ein kleiner Block:
- Ziel, Land, warum es passt (ein Satz zu den Interessen)
- Wetter im Reisemonat: Höchst- und Tiefstwert, Regentage
- Kosten grob: Flug, Hotel je Nacht, Essen je Tag, Summe für die Dauer, mit Quelle
- Sicherheitslage laut Auswärtigem Amt, mit Stand
- ein Haken (Anreise lang, Regenzeit, Visum nötig, Hochsaison)

Am Ende eine klare Empfehlung mit einem Satz Begründung und die Frage, welches Ziel weiter
geplant wird. Dann: `/reise-preise` für Flüge und Hotels, `/reise-tage` für die Tage vor
Ort, `/reise-einreise` für Papiere.
