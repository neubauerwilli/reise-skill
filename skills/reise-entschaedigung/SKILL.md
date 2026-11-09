---
name: reise-entschaedigung
description: >-
  Der Fluggast-Anwalt. Prüft bei Verspätung, Annullierung oder Nichtbeförderung, ob dir
  nach der EU-Fluggastrechte-Verordnung 261/2004 Geld zusteht (250, 400 oder 600 Euro je
  Person, nach Entfernung), prüft die Ausnahme außergewöhnlicher Umstand und schreibt den
  fertigen Antrag an die Airline. Nutze ihn, wenn der Nutzer sagt "Flug verspätet",
  "Flug annulliert", "Entschädigung", "Fluggastrechte", "Ausgleichszahlung", "mein Flug
  ist ausgefallen" oder "kriege ich Geld zurück".
argument-hint: "[Abflug] [Ziel] [Verspätung in Stunden] [Grund]"
---

# reise-entschaedigung

Bei einem verspäteten oder ausgefallenen Flug steht dir oft Geld zu, und die meisten
holen es nie ab. Dieser Skill rechnet es aus und schreibt den Antrag.

## Grundregeln

Keine Rechtsberatung. Du rechnest nach der Verordnung (EG) 261/2004 und schreibst einen
Antrag. **Abschicken tut der Nutzer**, und die IBAN trägt er selbst ein. Der Skill gibt
nie Zahlungsdaten ein und schickt nichts ab.

## Schritt 1: die Angaben

Frag nach, was fehlt:
- Abflughafen und Ziel (IATA-Code reicht, sonst der Stadtname)
- Datum, Flugnummer, Airline, Buchungsnummer
- Was ist passiert: **Verspätung bei der Ankunft** (nicht beim Abflug, es zählt, wann die
  Türen am Ziel aufgingen), **Annullierung** oder **Nichtbeförderung** (Überbuchung)
- Wie viele Stunden zu spät am Ziel
- Warum, laut Airline: technischer Defekt, Crew, Wetter, Flugsicherung, Streik
  (der eigenen Leute oder am Flughafen), Sicherheit, Vogelschlag, kein Grund genannt
- Bei Annullierung: wie viele Tage vorher mitgeteilt, ob ein Ersatzflug angeboten wurde
- Abflug in der EU, Island, Norwegen oder der Schweiz? Sonst: Sitzt die Airline in der EU?

## Schritt 2: rechnen

Das Werkzeug `anspruch.py` rechnet die Großkreis-Distanz zwischen den Flughäfen, die
Stufe und die Ausnahmen:

```bash
python3 skills/reise-entschaedigung/anspruch.py --von MUC --nach LIS --verspaetung 4 --grund technisch
python3 skills/reise-entschaedigung/anspruch.py --von FRA --nach JFK --art annullierung --vorwarnung-tage 3 --grund airline
```

Unter Windows heißt der Aufruf oft `py` statt `python3`. Gründe: `technisch`, `airline`,
`crew`, `streik-airline`, `unbekannt`, `wetter`, `flugsicherung`, `streik-flughafen`,
`sicherheit`, `vogelschlag`. Bei Annullierung mit Ersatzflug `--ersatzflug --frueher <Std>`
und `--verspaetung <Std Verspätung des Ersatzflugs>` angeben. Ist ein Flughafen nicht in der
eingebauten Tabelle, nimm `--von-koord "lat,lon"` oder den Ortsnamen (Näherung, sag das dazu).
Ohne Python: rechne selbst nach der Tabelle unten.

Die Stufen je Fluggast:

| Entfernung | Betrag |
| --- | --- |
| bis 1.500 km | 250 Euro |
| über 1.500 km innerhalb der EU, sonst 1.500 bis 3.500 km | 400 Euro |
| über 3.500 km außerhalb der EU | 600 Euro |

Bei Verspätung gilt der Anspruch ab **3 Stunden** am Ziel. Über 3.500 km und unter 4 Stunden
darf die Airline auf die Hälfte kürzen.

## Schritt 3: außergewöhnliche Umstände

Die Airline zahlt nicht, wenn sie einen außergewöhnlichen Umstand beweist, den sie auch mit
allen zumutbaren Mitteln nicht hätte vermeiden können. Meist gilt:
- **Kein Ausweg für die Airline:** technischer Defekt, Crew fehlt, Umlaufplanung, Streik der
  eigenen Belegschaft, Überbuchung.
- **Meist ein Ausweg:** Unwetter, Flugsicherung, Streik am Flughafen, Sicherheitslage,
  Vogelschlag.
Das ist Rechtsprechung im Fluss. Sag dem Nutzer offen, wo es ein Grenzfall ist (zum Beispiel
bei einem Defekt durch ein Fremdteil auf der Piste), und lass ihn den Antrag trotzdem
stellen, wenn der Grund unklar ist: Die Airline muss ihn nachweisen.

## Schritt 4: der Antrag

```bash
python3 skills/reise-entschaedigung/anspruch.py ... --antrag reise/antrag.txt --name "Vor Nachname" --airline <Airline> --flugnr <Nr> --datum <JJJJ-MM-TT> --buchung <Code>
```

Das Werkzeug schreibt einen sachlichen Antrag mit Verordnung, Betrag, Frist und Zahlungsbitte.
Zeig ihn dem Nutzer, ergänze Rest-Platzhalter und sag ihm klar:
1. Du schickst ihn selbst ab, an das Formular oder die Mailadresse der Airline.
   Hol die aktuelle Adresse per Websuche (Suche: `<Airline> Fluggastrechte Formular`) und
   nenne sie mit Abrufdatum.
2. Belege anhängen: Bordkarte, Buchungsbestätigung, Nachweis der Verspätung (zum Beispiel
   Flugstatus-Seite), Belege für Essen oder Hotel.
3. Antwortet die Airline nicht oder lehnt ab: Schlichtungsstelle (Deutschland: söp,
   Österreich: Agentur für Passagier- und Fahrgastrechte, Schweiz: Schlichtungsstelle des
   Bundes) oder Fluggastrechte-Portal. Hol die Adresse per Websuche.
4. Die Verjährung ist je nach Land verschieden (in Deutschland drei Jahre zum Jahresende).
   Prüf sie für das Land des Nutzers per Websuche, bevor du etwas versprichst.

## Immer dazu sagen

Unabhängig vom Ausgleich hat der Fluggast bei Verspätung ab bestimmter Dauer Anspruch auf
Betreuung (Essen, Getränke, Hotel, Transfer), und bei Annullierung auf Erstattung oder
Ersatzflug. Das gilt auch, wenn der Ausgleich wegen eines außergewöhnlichen Umstands
entfällt.
