---
name: reise-einreise
description: >-
  Der Einreise-Prüfer. Prüft Pass oder Ausweis, Visum, Impfungen und Sicherheitslage für ein
  Reiseziel mit Stand-Datum der Quelle. Nutze ihn, wenn der Nutzer sagt "brauche ich ein
  Visum", "Einreisebestimmungen", "Reisepass", "Impfung", "Reisewarnung", "ist es sicher
  dort" oder "Einreise nach Thailand".
argument-hint: "[Zielland] [Staatsangehörigkeit]"
---

# reise-einreise

Ein abgelaufener Pass oder ein fehlendes Visum kostet die ganze Reise. Dieser Skill prüft
vor dem Buchen.

## Grundregeln

Einreise- und Sicherheitsangaben **nie aus dem Gedächtnis**, immer aus einer Quelle mit
Stand-Datum und Abrufzeit. Keine Rechtsberatung. Bucht und beantragt nichts selbst, gibt
keine Passdaten in Formulare ein. Ergebnis nach `reise/einreise.md`.

## Schritt 1: fragen

Zielland (auch Zwischenstopps), Staatsangehörigkeit (Deutschland, Österreich, Schweiz,
andere), Dokument (Reisepass, Personalausweis), Ablaufdatum, Reisedatum, Aufenthaltsdauer,
Zweck (Urlaub, Arbeit), Kinder mit eigenem Dokument?

## Schritt 2: Quelle holen

**Deutsche Staatsangehörige:** 
```bash
python3 skills/reise-einreise/aa.py Thailand
python3 skills/reise-einreise/aa.py TH --abschnitt "Einreise" --abschnitt "Impf"
```
Das Werkzeug liest die Reise- und Sicherheitshinweise des Auswärtigen Amts (OpenData, kein
Schlüssel) und zeigt Reisewarnung, Teilwarnung, Stand-Datum und die Abschnitte zu Einreise,
Zoll, Gesundheit und Impfungen. Unter Windows heißt der Aufruf oft `py`.

**Österreich und Schweiz:** Hol per Websuche und Seitenabruf die Seiten des BMEIA
(`reiseinformation` auf bmeia.gv.at) oder des EDA (Reisehinweise auf eda.admin.ch). Das
Auswärtige Amt gilt für Deutsche, nicht für andere Staatsangehörige: Sag das.

**Andere Staatsangehörigkeit:** Sag, dass die Regeln abweichen, und such die Seite des
Außenministeriums des Nutzers.

Prüf bei Visum und Einreise zusätzlich die Seite der Botschaft des Ziellandes, denn sie
ist verbindlich. Elektronische Genehmigungen (etwa ESTA, eTA, ETIAS, e-Visa): nenne, dass
es sie gibt, und verweise auf die amtliche Seite. Warne vor Vermittlern, die Gebühren
aufschlagen.

## Schritt 3: die Antwort

- **Dokument:** Pass oder Ausweis, Mindestgültigkeit bei Einreise (zum Beispiel sechs
  Monate über das Reiseende), freie Seiten.
- **Visum:** nötig oder nicht, wie lange erlaubt, wo beantragt, Kosten, Bearbeitungszeit.
- **Impfungen:** vorgeschrieben, empfohlen, mit Quelle.
- **Sicherheitslage:** Reisewarnung ja oder nein, Teile des Landes, Stand-Datum.
- **Zoll und Sonstiges:** Medikamente, Drohnen, Bargeld, Einfuhrverbote, wenn in der Quelle.

Immer: "Quelle: <Seite>, Stand <Datum der Quelle>, abgerufen <Datum Uhrzeit>. Einreiseregeln
ändern sich kurzfristig: prüf eine Woche vor Abflug noch einmal." Frist-Dinge (Visum beantragen,
Impfung ansetzen) in die Checkliste von `/reise-buchung`.
