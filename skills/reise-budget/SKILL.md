---
name: reise-budget
description: >-
  Der Budget-Rechner. Rechnet die Gesamtkosten der Reise aus Flug, Hotel, Essen vor Ort und
  Transfers in Euro und in Landeswährung und gibt ein Tageslimit. Nutze ihn, wenn der
  Nutzer sagt "was kostet die Reise", "Budget", "wie viel Geld brauche ich", "Tageslimit",
  "umrechnen in Dollar" oder "reicht mein Geld".
argument-hint: "[Ziel] [Tage] [Budget in Euro]"
---

# reise-budget

Der Flug ist nie der ganze Preis. Dieser Skill rechnet die ganze Reise und sagt, wie viel
du am Tag ausgeben kannst.

## Grundregeln

Bucht nichts, gibt keine Zahlungsdaten ein. Wechselkurse mit Datum und Quelle, Preisniveau
vor Ort mit Quelle und Abrufzeit und als Momentaufnahme. Ergebnis nach `reise/budget.md`.

## Schritt 1: die Zahlen sammeln

Aus den anderen Skills (`reise/preise.md`, `reise/ziele.md`) oder per Frage: Anzahl Tage,
Flugpreis gesamt, Hotelpreis je Nacht, Transfers (Flughafen, Bahn, Mietwagen), Eintritte,
Gesamtbudget, Landeswährung.

**Essen und Alltag vor Ort:** Such per Websuche das Preisniveau am Ziel (zum Beispiel
Numbeo, Reiseblogs, Reiseführer, Tagesbudget-Angaben) und nenn Quelle und Abrufzeit. Gib
eine Spanne (sparsam, mittel, großzügig) statt einer Zahl.

## Schritt 2: rechnen

```bash
python3 skills/reise-budget/budget.py --waehrung THB --tage 10 --flug 780 --hotel-nacht 65 --essen-tag 25 --transfer 90 --budget 2000
```

Alle Beträge in Euro. Das Werkzeug holt den EZB-Referenzkurs über Frankfurter
(`api.frankfurter.dev`, kein Schlüssel), nennt das Kursdatum, rechnet alle Posten in Euro und
Landeswährung und gibt das Tageslimit für Essen und Alltag. Währungen, die die EZB nicht
führt, fehlen: Dann Kurs per Websuche mit Quelle holen. Unter Windows heißt der Aufruf oft
`py`.

## Schritt 3: die Antwort

Tabelle mit Posten in Euro und Landeswährung, Summe, Tageslimit, ein Satz dazu, ob das
Budget reicht und wo es eng wird. Rechne drei Fälle (sparsam, mittel, großzügig). Plane
einen Puffer ein, zum Beispiel zehn Prozent. Hinweise: Gebühren der Karte im Ausland,
Bargeldabheben, Trinkgeld (`/reise-vor-ort`). Kurse ändern sich: vor der Reise neu rechnen.
