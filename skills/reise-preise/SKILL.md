---
name: reise-preise
description: >-
  Der Preis-Vergleicher. Vergleicht Flüge und Hotels für ein Ziel und einen Zeitraum, nennt
  die günstigsten Tage und Unterkünfte mit Link, Preis, Quelle und Abrufzeit. Nutze ihn, wenn
  der Nutzer sagt "Flüge vergleichen", "günstigster Flug", "Hotel finden", "wann ist es am
  billigsten", "Flug und Hotel nach Lissabon" oder "was kostet die Reise".
argument-hint: "[Abflug] [Ziel] [von] [bis]"
---

# reise-preise

Du sparst nicht durch Raten, sondern durch Vergleichen. Dieser Skill vergleicht live und
nennt jeden Preis mit Beleg.

## Grundregeln

**Bucht nie, zahlt nie, gibt nie Zahlungs- oder Passdaten ein.** Du liest Preise und gibst
Links. Jeder Preis bekommt: Quelle, Link, Abrufzeit und den Hinweis "Momentaufnahme".
Preise nie schätzen oder aus dem Gedächtnis nennen: Was du nicht gelesen hast, steht nicht
in der Tabelle. Ergebnis nach `reise/preise.md`.

## Schritt 1: die Angaben

Abflughafen (oder mehrere in der Nähe), Ziel, Zeitraum, Flexibilität (plus minus drei Tage?),
Anzahl Personen, Gepäck (nur Handgepäck?), direkt oder mit Stopp, Hotel-Wünsche (Lage,
Sterne, Frühstück, Höchstpreis je Nacht).

## Schritt 2: Links bauen, mit den drei Spar-Hebeln

```bash
python3 skills/reise-preise/preise.py links --von BER --nach LIS --ab 2027-03-10 --bis 2027-03-17 --ort Lissabon --personen 2 --umkreis 150 --flexibel 3
```

Das Werkzeug baut Suchlinks für Google Flights, Skyscanner, Booking.com und Google Hotels
(IATA-Codes, Daten als JJJJ-MM-TT). Es ruft keine Preise ab. Drei Hebel, die oft den
größten Unterschied machen:

1. **Umkreis** (`--umkreis KM`, Standard 150): Links für alle Flughäfen im Umkreis des
   Abflughafens aus der eingebauten Tabelle (Deutschland, Österreich, Schweiz, Nachbarn). Von
   Berlin aus sind das zum Beispiel Leipzig und Dresden. Ist der Flughafen nicht in der
   Tabelle, sagt das Werkzeug es: Dann nennst du die Flughäfen in der Nähe selbst per Websuche.
   Der Preisunterschied muss die Anfahrt tragen: Rechne Bahn oder Auto hin und zurück dagegen.
2. **Flexibel** (`--flexibel N`): Links für jedes Datum im Fenster plus minus N Tage bei
   gleicher Reisedauer, dazu die Monatsansicht (Skyscanner Monat, Google Flights Datumsgitter,
   dort das Datumsfeld anklicken). So findest du den günstigsten Tag statt den Wunschtag.
3. **Hotels nach Preis-Leistung:** der Booking-Link kommt zusätzlich mit Bewertungsfilter
   (Standard ab 8,0, mit `--min-bewertung` änderbar). Gewertet wird später die Bewertung je
   100 Euro, nicht der niedrigste Preis.

## Schritt 3: Preise lesen

Wege, in dieser Reihenfolge:
1. **Claude in Chrome**, wenn der Nutzer es verbunden hat: öffne die Links, lies die
   Ergebnisseite, nimm Preis, Zeiten, Anbieter, Gepäckregel. Du klickst nie auf "Buchen"
   und gibst nichts in Buchungsformulare ein.
2. **Abruf öffentlicher Seiten** per Websuche und Seitenabruf: Viele Preisseiten laden Preise
   erst per Skript und sind dann nicht lesbar. Sag das offen, statt etwas zu erfinden.
3. Klappt beides nicht: Gib dem Nutzer die Links und bitte ihn, die drei günstigsten Treffer
   zu nennen oder einen Screenshot zu zeigen. Dann arbeitest du damit weiter.

Probiere bei Flexibilität mehrere Wochentage (Dienstag und Mittwoch sind oft günstiger als
Freitag und Sonntag) und nenne die günstigsten Tage. Beim Hotel: Preis je Nacht und
Gesamtpreis, Stornobedingung, Lage zum Zentrum.

## Schritt 4: die Tabelle mit Ersparnis

Schreib die gefundenen Angebote in `reise/angebote.json` (siehe `beispiel/angebote.json`).
Flüge: art, flughafen, tag (JJJJ-MM-TT), quelle, titel, preis (Gesamtpreis in Euro), link,
abgerufen (Datum und Uhrzeit). Hotels: dieselben Felder plus `bewertung` (0 bis 10). Markiere
den Treffer, den der Nutzer ohne Vergleich genommen hätte, mit `"standard": true` (der
Wunschtermin am Hauptflughafen, das erste Hotel der Suche). Dann:

```bash
python3 skills/reise-preise/preise.py tabelle reise/angebote.json --haupt BER --min-bewertung 8.0
```

Das Werkzeug zeigt:
- Flüge, günstigste zuerst, mit Spalten Tag und Flughafen, der günstigste markiert
- Preis je Flughafen gegen den Hauptflughafen ("spart 65 Euro gegen BER")
- Hotels nach Preis-Leistung (Bewertung je 100 Euro), Häuser unter der Mindestbewertung
  ausgeschlossen, Häuser ohne Bewertung nicht gewertet
- die Ersparnis-Zeile: "statt 289 Euro nur 176 Euro" für Flug und Hotel gegen den
  Standardtreffer

Zeig dem Nutzer die drei günstigsten Flüge, die drei besten Hotels und die Ersparnis-Zeile,
mit Link, Preis, Quelle, Abrufzeit. Sag ehrlich dazu, was die Ersparnis kostet (Anfahrt zum
anderen Flughafen, anderer Wochentag, etwas niedrigere Bewertung). Nenn nie eine Ersparnis,
die nicht aus gelesenen Preisen stammt. Dann klar: Preise ändern sich laufend, gebucht
wird nur von dir, die Reihenfolge fürs Buchen macht `/reise-buchung`. Danach `/reise-budget`.

## Bewertungs-Check: das Hotel, das für dein Geld am meisten bietet

Die Durchschnittsnote allein sagt wenig. Lies, was die Gäste wirklich schreiben, bevor der
Nutzer ein Hotel wählt. Mach das für die zwei bis drei Hotels vorn in der Preis-Leistungs-
Liste aus Schritt 4.

1. **Bewertungen lesen.** Per Claude in Chrome (wenn verbunden) oder Websuche und Seitenabruf
   auf Booking, Google und Tripadvisor. Lies mindestens zehn Bewertungen je Hotel aus den
   letzten zwölf Monaten, die kritischen und die guten gemischt, in mehr als einer Quelle.
   Du öffnest nur Lese-Seiten, loggst dich nie ein und schreibst nie eine Bewertung. Lassen
   sich Bewertungen nicht lesen (Seite lädt per Skript), sag das und bitte den Nutzer um
   Screenshots. Erfinde nie eine Bewertung.
2. **In eine Datei schreiben.** Je Hotel name, preis, bewertung, quelle, abgerufen und je
   Bewertung quelle, datum, sterne, text (Wortlaut, gekürzt auf das Wesentliche). Format siehe
   `beispiel/bewertungen.json`.
3. **Zählen lassen:**
   ```bash
   python3 skills/reise-preise/bewertungen.py reise/bewertungen.json --min-bewertung 8.0
   ```
   Das Werkzeug zählt je Thema (Sauberkeit, Zustand, Lage, Lärm, Personal, Frühstück,
   Ungeziefer) Lob und Kritik, zeigt wiederkehrende Beschwerden mit Beispielsatz, prüft, wie
   viele Gäste "sieht aus wie auf den Fotos" bestätigen oder bestreiten, rechnet die
   Preis-Leistung (Bewertung je 100 Euro) und gibt ein vorläufiges Urteil. Es ist eine
   Stichwortzählung in Deutsch und Englisch, keine Sprachanalyse: Lies die genannten Belege
   selbst gegen, bevor du etwas behauptest.
4. **Urteil schreiben.** Je Hotel in drei Sätzen: Was Gäste loben, was wiederholt bemängelt
   wird (mit Zahl, zum Beispiel "3 von 7 nennen Lärm"), ob es auf den Fotos so aussieht
   wie in echt. Dann: empfehlen, mit Vorbehalt oder nicht empfehlen, mit Preis-Leistung.
   Die billigste Unterkunft ist nicht automatisch die beste: Ungeziefer, Schimmel oder
   Fotos, die mehrere Gäste als irreführend nennen, sind ein Grund, sie auszuschließen,
   auch wenn die Rechnung gut aussieht. Gib bei wenig Bewertungen offen zu, dass die Basis
   dünn ist.

Nenn zu jeder Aussage Quelle und Abrufzeit. Bewertungen ändern sich: Das ist eine
Momentaufnahme.
