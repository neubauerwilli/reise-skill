# Der Reise-Skill

Elf Claude-Skills auf Deutsch, die dein Reisebüro ersetzen. Kostenlos, MIT, keine
Anmeldung, kein API-Schlüssel, nichts zu verbinden. Deine Reisepläne bleiben in einem Ordner
auf deinem Rechner.

Einer schlägt dir Ziele zu deinem Budget vor. Einer vergleicht Flüge und Hotels. Einer plant
jeden Tag vor Ort, mit Plätzen, die sonst nur Einheimische kennen. Einer macht aus einem
Instagram-Reel eine fertige Reise. Und wenn dein Flug ausfällt, rechnet einer aus, wie viel
Geld dir zusteht, und schreibt den Antrag.

**Gebucht oder bezahlt wird nichts, bevor du Ja sagst.** Kein Skill bucht, zahlt oder gibt
Zahlungsdaten ein. Das machst du selbst.

> Keine Rechts- oder Reiseberatung im Rechtssinn. Preise sind Momentaufnahmen und kommen mit
> Quelle und Abrufzeit. Einreise- und Sicherheitsangaben kommen aus amtlichen Quellen mit
> Stand-Datum, nie aus dem Gedächtnis.

## Einrichten

Füge den Link zu diesem Repo in Claude ein und sag `install skill`:

```
https://github.com/neubauerwilli/reise-skill

install skill
```

Oder als Plugin in Claude Code:

```
/plugin marketplace add neubauerwilli/reise-skill
/plugin install reise-skill@reise-skill
```

Als Plugin bekommen die Skills einen Namensraum, sie heißen dann `/reise-skill:reise-ziel`
und so weiter. Wenn du einfach `/reise-ziel` willst, kopiere die Ordner:

```bash
git clone https://github.com/neubauerwilli/reise-skill.git
cp -r reise-skill/skills/reise-* ~/.claude/skills/
```

Windows (PowerShell):

```powershell
git clone https://github.com/neubauerwilli/reise-skill.git
Copy-Item -Recurse reise-skill\skills\reise-* "$env:USERPROFILE\.claude\skills\"
```

Kein Claude Code? Füge eine einzelne `SKILL.md` oben in einen Chat ein, dann läuft sie als
Modus. Die Python-Werkzeuge fallen dann weg, die Methode funktioniert trotzdem.

Die Werkzeuge brauchen Python 3.8 oder neuer, nichts per pip installieren. Unter Windows heißt
der Aufruf oft `py` statt `python3`. Für Standbilder aus Videos (`reise-reel`) brauchst du
zusätzlich ffmpeg und yt-dlp.

## Die elf

| Befehl | Rolle | Was er macht |
| --- | --- | --- |
| `/reise-ziel` | Ziel-Finder | Fragt Budget, Zeit, Abflughafen und Interessen, schlägt drei bis fünf Ziele vor mit Wetter, Kosten und Sicherheitslage. Werkzeug: `ziel.py`. |
| `/reise-preise` | Preis-Vergleicher | Vergleicht Flüge und Hotels: Flughäfen im Umkreis, flexible Tage, Preis-Leistung bei Hotels, Ersparnis-Zeile. Jeder Preis mit Link, Quelle und Abrufzeit. Dazu der Bewertungs-Check (`bewertungen.py`): liest Gästebewertungen, zählt wiederkehrende Beschwerden, prüft ob es wie auf den Fotos aussieht. Werkzeug: `preise.py`. |
| `/reise-tage` | Tagesplaner | Plant jeden Tag vor Ort mit Wegzeiten, Öffnungszeiten und Plätzen aus lokalen Quellen, je Tag ein Kartenlink. Werkzeug: `route.py`. |
| `/reise-reel` | Reel-Skill | Erkennt den Ort aus Reel, Screenshot oder Foto und plant Flug, Hotel und Route dorthin. Werkzeug: `frames.py`. |
| `/reise-einreise` | Einreise-Prüfer | Pass, Visum, Impfungen und Sicherheitslage mit Stand-Datum. Werkzeug: `aa.py`. |
| `/reise-packliste` | Packlisten-Bauer | Liste aus Ziel, Wetter, Dauer und Aktivitäten, dazu die Gepäckregeln der Airline. Werkzeug: `packliste.py`. |
| `/reise-buchung` | Buchungs-Lotse | Reihenfolge und Fristen fürs Buchen als Checkliste. Bucht selbst nichts. |
| `/reise-budget` | Budget-Rechner | Gesamtkosten in Euro und Landeswährung, Tageslimit. Werkzeug: `budget.py`. |
| `/reise-feiertage` | Feiertags-Warner | Feiertage, Festivals und Ferien am Ziel im Reisezeitraum. Werkzeug: `feiertage.py`. |
| `/reise-entschaedigung` | Fluggast-Anwalt | Prüft Anspruch nach der EU-Verordnung 261/2004 (250, 400 oder 600 Euro) und schreibt den Antrag. Werkzeug: `anspruch.py`. |
| `/reise-vor-ort` | Reisebegleiter | Sätze in der Landessprache, Speisekarte per Foto, Trinkgeld, Notrufnummern. |

## So nutzt du ihn

Fang mit `/reise-ziel` an, oder schick `/reise-reel` ein Reel von einem Ort, der dich nicht
loslässt. Jeder Skill liest und schreibt in `reise/` in deinem Projekt:

```
reise/
├── ziele.md  ·  preise.md  ·  angebote.json
├── tage.md  ·  tage.json
├── reel.md  ·  frames/
├── einreise.md  ·  packliste.md  ·  budget.md  ·  feiertage.md
├── buchung.md
└── antrag.txt
```

## Datenquellen

Alles frei, ohne Schlüssel: Auswärtiges Amt OpenData (Reise- und Sicherheitshinweise),
Open-Meteo (Wetter und Klima), Nager.Date (Feiertage), Frankfurter (EZB-Wechselkurse),
OpenStreetMap Nominatim (Ortssuche, höchstens eine Anfrage je Sekunde), dazu die
Websuche in Claude. Optional Claude in Chrome, um Preisseiten live zu lesen.

## Datenschutz

Alles läuft in deinem Projektordner. Gib Claude nie Passnummer, IBAN oder Kartendaten: Für
die Planung werden sie nie gebraucht. Was du Claude zeigst, geht an deinen Claude-Zugang,
wie jede andere Unterhaltung auch.

## Ausprobieren ohne eigene Daten

Im Ordner [`beispiel`](beispiel/) liegen Beispieldateien (Preise und Bewertungen sind erfunden):

```bash
python3 skills/reise-ziel/ziel.py Lissabon --monat 3
python3 skills/reise-tage/route.py beispiel/tage.json
python3 skills/reise-preise/preise.py links --von BER --nach LIS --ab 2027-03-10 --bis 2027-03-17 --ort Lissabon --umkreis 150 --flexibel 3
python3 skills/reise-preise/preise.py tabelle beispiel/angebote.json --haupt BER
python3 skills/reise-preise/bewertungen.py beispiel/bewertungen.json
python3 skills/reise-entschaedigung/anspruch.py --von MUC --nach LIS --verspaetung 4 --grund technisch
python3 skills/reise-feiertage/feiertage.py --land PT --von 2027-04-01 --bis 2027-04-30
```

Drei fertige Fälle für den Entschädigungs-Rechner stehen in
[`beispiel/entschaedigung-faelle.md`](beispiel/entschaedigung-faelle.md).

Von Willi Neubauer · Lizenz: [MIT](LICENSE)
