---
name: reise-buchung
description: >-
  Der Buchungs-Lotse. Legt die Reihenfolge fürs Buchen fest (was zuerst, was stornierbar,
  welche Fristen) als Checkliste mit Links. Bucht selbst nichts. Nutze ihn, wenn der Nutzer
  sagt "wie buche ich das", "was zuerst buchen", "Reihenfolge Buchung", "stornierbar",
  "Fristen vor der Reise" oder "ich bin bereit zu buchen".
argument-hint: "[Reise in einem Satz]"
---

# reise-buchung

Bei der Buchung geht Geld verloren, wenn die Reihenfolge nicht stimmt: Flug gebucht, Visum
nicht bekommen. Dieser Skill ordnet die Schritte und legt die Fristen fest.

## Grundregeln

**Du buchst nie, zahlst nie und gibst nie Zahlungs-, Pass- oder Kontodaten ein.** Du
legst die Reihenfolge fest und gibst Links, der Nutzer klickt und zahlt selbst. Kein
Skill beschafft Zugänge. Nur ein klares Ja des Nutzers macht aus der Checkliste den
nächsten Schritt, und auch dann gehst du nur mit, wenn er die Buchung selbst durchführt.
Ergebnis nach `reise/buchung.md`.

## Schritt 1: den Stand klären

Lies die vorhandenen Dateien in `reise/` (Ziele, Preise, Tage, Einreise). Frag, was
feststeht: Ziel, Datum, Personen, Flug und Hotel gewählt, Budget, Flexibilität.

## Schritt 2: die Reihenfolge

Setze die Schritte in diese Ordnung und passe sie an:
1. **Vorbedingungen klären:** Pass gültig, Visum oder Einreisegenehmigung nötig (Fristen mit
   `/reise-einreise`), Urlaub genehmigt, Mitreisende einig.
2. **Mit stornierbarem Hotel anfangen:** kostenlose Stornierung bis zu einer Frist, die du
   mit Datum nennst. Das hält den Termin offen, ohne dass Geld verloren geht.
3. **Flug buchen**, sobald Visum und Termin sicher sind: Tarif mit Umbuchung oder Storno
   prüfen, Gepäck, Namen genau wie im Pass.
4. **Transfers und Mietwagen** (Mietwagen mit kostenloser Stornierung).
5. **Eintritte und Restaurants**, die ausverkaufen können (nur mit Stornofrist).
6. **Versicherung:** Reiserücktritt und Auslandskranken nach dem Flug, vor der ersten
   Stornogebühr. Beschreibe, worauf es ankommt (Selbstbehalt, Vorerkrankungen), und
   empfiehl kein bestimmtes Produkt.
7. **Vor der Abreise:** Online-Check-in (meist 24 bis 48 Stunden vorher), Ausweis, Handy,
   Bargeld, Nachweise ausdrucken oder offline speichern.

## Schritt 3: die Fristen-Liste

Schreib eine Tabelle: Schritt, Frist (Datum), stornierbar bis, Link, Kosten bei Storno. Hol
Fristen und Stornobedingungen von den Seiten der Anbieter per Websuche, mit Abrufdatum,
und rate nie. Gibt es keinen Beleg, schreib "prüfen auf Seite X".

## Schritt 4: die Antwort

Gib die Checkliste mit Links und frag, welcher Schritt dran ist. Sag den Satz ausdrücklich:
**Gebucht wird nur von dir.** Wer eine Frist verpasst, verliert Geld: Biete an, die Fristen
als Kalenderdatei zu schreiben (`.ics`) oder Erinnerungen im Kalender zu setzen, aber nur,
wenn der Nutzer es will.
