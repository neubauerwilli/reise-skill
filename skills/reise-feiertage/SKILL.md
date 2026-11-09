---
name: reise-feiertage
description: >-
  Der Feiertags-Warner. Warnt vor Feiertagen und großen Veranstaltungen am Ziel im
  Reisezeitraum: geschlossene Läden, volle Hotels, höhere Preise. Nutze ihn, wenn der Nutzer
  sagt "Feiertage am Ziel", "ist da dann alles zu", "Hochsaison", "Festival", "Ferien" oder
  "wann ist es dort voll".
argument-hint: "[Land] [von] [bis]"
---

# reise-feiertage

Nichts ist ärgerlicher als vor einer geschlossenen Sehenswürdigkeit zu stehen, weil am
Reisetag Feiertag ist, oder zu merken, dass die Stadt wegen eines Festivals doppelt so
teuer ist.

## Grundregeln

Bucht nichts, gibt keine Zahlungsdaten ein. Alle Daten mit Quelle und Abrufzeit. Ergebnis
nach `reise/feiertage.md`.

## Schritt 1: Feiertage

```bash
python3 skills/reise-feiertage/feiertage.py --land PT --von 2027-04-01 --bis 2027-04-14
```

Das Werkzeug fragt Nager.Date ab (kein Schlüssel) und zeigt gesetzliche Feiertage im
Zeitraum, mit Hinweis, ob sie landesweit oder nur in Regionen gelten. Land als ISO-Code
(PT, TH, US). Kennt Nager.Date das Land nicht, meldet das Werkzeug es: Dann Websuche. Unter
Windows heißt der Aufruf oft `py`.

## Schritt 2: das, was Nager nicht kennt

Per Websuche für Ziel und Zeitraum prüfen:
- religiöse Festzeiten ohne gesetzlichen Feiertag (Ramadan, Songkran, Karneval,
  Semana Santa, Diwali, Neujahr nach dem Mondkalender)
- Messen, Kongresse, Konzerte, Sportereignisse und Festivals in der Stadt
- Ferien der Einheimischen (Hochsaison, volle Strände)
- Ruhetage großer Sehenswürdigkeiten

Nenne jede Aussage mit Quelle und Datum.

## Schritt 3: die Antwort

Je betroffenem Tag: Datum, was los ist, was es bedeutet (Läden zu, Verkehr, Preise hoch,
Hotels ausgebucht), Empfehlung (verschieben, vorbuchen, ausweichen, als Erlebnis nutzen).
Sag klar, ob eine Verschiebung des Reisezeitraums um wenige Tage etwas spart. Das Ergebnis
geht an `/reise-tage` (Tage umlegen) und `/reise-preise` (günstigere Tage).
