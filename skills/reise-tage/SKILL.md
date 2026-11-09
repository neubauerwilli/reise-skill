---
name: reise-tage
description: >-
  Der Tagesplaner. Plant jeden Tag vor Ort mit Orten, Wegzeiten, Öffnungszeiten und Plätzen,
  die sonst nur Einheimische kennen, aus Blogs, Foren und Bewertungen. Je Tag ein
  Google-Maps-Link. Nutze ihn, wenn der Nutzer sagt "plan meine Tage", "was mache ich in
  Lissabon", "Tagesplan", "Reiseroute", "Geheimtipps" oder "Sehenswürdigkeiten".
argument-hint: "[Stadt oder Region] [Anzahl Tage] [Interessen]"
---

# reise-tage

Kein Tag nach Reiseführer-Schablone, sondern eine Route, die geografisch Sinn ergibt und
Orte enthält, an denen nicht jeder Tourist steht.

## Grundregeln

Bucht und reserviert nichts selbst, gibt keine Zahlungsdaten ein. Öffnungszeiten und Preise
immer mit Quelle und Abrufdatum, und sag dazu: vor dem Besuch auf der Seite des Ortes prüfen.
Nichts erfinden: Findest du keinen Beleg für einen Ort, nimm ihn nicht auf. Ergebnis nach
`reise/tage.md`.

## Schritt 1: fragen

Ziel, Anzahl Tage, Ankunfts- und Abreisezeit (erster und letzter Tag sind kurz), Interessen
(Essen, Kultur, Natur, Nachtleben), Tempo (viel sehen oder entspannt), Mobilität, Kinder,
Budget für Eintritte, Unterkunftslage (Viertel).

## Schritt 2: Orte sammeln

Websuche in drei Schichten:
1. **Das Muss:** die Orte, die jeder nennt (kurz halten, höchstens ein bis zwei je Tag).
2. **Einheimische Quellen:** lokale Blogs, Foren (zum Beispiel Reddit des Ortes), Bewertungen
   mit vielen Rezensionen von Einheimischen, Lokalzeitungen. Suche auch in der Landessprache
   (`bestes <Gericht> <Stadt> locals`, `<Stadt> versteckte Plätze Blog`).
3. **Praktisches:** Öffnungszeiten, Ruhetage, Reservierung nötig, Eintritt.

Wirf aus, was nur eine Quelle empfiehlt und sonst nirgends vorkommt, und nenne bei jedem
Geheimtipp, woher er stammt.

## Schritt 3: pro Tag eine Route

Schreib `reise/tage.json` mit Stadt und je Tag Titel und Orten (siehe `beispiel/tage.json`),
dann:

```bash
python3 skills/reise-tage/route.py reise/tage.json
```

Das Werkzeug sucht die Koordinaten über OpenStreetMap Nominatim (höchstens eine Anfrage je
Sekunde, deshalb dauert es), bringt die Orte in eine kurze Reihenfolge, schätzt die Fußwege
und baut je Tag einen Google-Maps-Link. Fehlen Orte, schreib die Namen genauer (mit Straße
oder Viertel). Wege über 2 km oder mit Steigung: schlag Bahn, Bus oder Taxi vor. Unter
Windows heißt der Aufruf oft `py`.

## Schritt 4: die Antwort

Je Tag: Titel, Orte in Reihenfolge mit Uhrzeit-Vorschlag, Wegzeiten, ein Satz was dort zu tun
ist, Essen am Mittag und Abend (ein Ort mit Quelle), Öffnungszeiten, Kartenlink, Reserve für
schlechtes Wetter. Der letzte Tag bleibt locker. Am Ende die Frage, was getauscht werden soll.
Dann `/reise-packliste` und `/reise-budget`.
