---
name: reise-reel
description: >-
  Der Reel-Skill. Nimmt einen Reel-Link, einen Screenshot oder ein Foto von einem Ort, den
  der Nutzer gesehen hat, erkennt den Ort, sagt wie sicher er ist, fragt bei Zweifel nach und
  übergibt an reise-preise und reise-tage. Am Ende stehen Flug, Hotel und Tagesroute zu genau
  diesem Ort. Nutze ihn, wenn der Nutzer sagt "wo ist das", "ich habe ein Reel gesehen",
  "dieser Ort", "da will ich hin", "Screenshot von Instagram" oder ein Bild oder Video von
  einem Reiseziel zeigt.
argument-hint: "[Reel-Link, Screenshot oder Foto]"
---

# reise-reel

Das Reel vom Traumort, das du gespeichert und nie gebucht hast. Hier wird daraus eine Reise.

## Grundregeln

Bucht nie, zahlt nie, gibt keine Zahlungsdaten ein. Der Ort wird nie geraten: Du nennst
deine Sicherheit offen und fragst bei Zweifel nach. Preise nur mit Quelle und Abrufzeit.
Ergebnis nach `reise/reel.md`.

## Schritt 1: Material holen

- **Screenshot oder Foto:** Lies das Bild direkt mit deiner Bilderkennung.
- **Videodatei:** Zieh Standbilder (braucht ffmpeg):
  ```bash
  python3 skills/reise-reel/frames.py reel.mp4 --anzahl 6 --out reise/frames
  ```
- **Link zu einem öffentlichen Reel:** Das gleiche Werkzeug lädt es ohne Anmeldung per
  yt-dlp und zieht die Bilder:
  ```bash
  python3 skills/reise-reel/frames.py "https://www.instagram.com/reel/XXXX/" --out reise/frames
  ```
  Klappt der Link nicht (privat, gesperrt, yt-dlp fehlt), sag das und bitte um einen
  Screenshot. Gib dich nie mit einem Login des Nutzers zufrieden: Du fragst nie nach
  Passwörtern.

Öffne die Bilder und schau sie an. Lies auch die Caption, Ortsmarke und Kommentare, wenn der
Nutzer sie mitgibt: Dort steht oft der Ortsname.

## Schritt 2: den Ort erkennen

Sammle Belege, bevor du dich festlegst:
1. **Schrift im Bild:** Straßenschilder, Läden, Speisekarten, Kennzeichen, Sprache.
2. **Wahrzeichen und Landschaft:** Küstenform, Felsen, Architektur, Vegetation, Brücken.
3. **Text zum Reel:** Ortsmarke, Hashtags, Caption.
4. **Websuche zur Bestätigung:** Such mit den Merkmalen (`Klippe türkises Wasser weißes Dorf
   Terrassenhäuser`, Name aus der Ortsmarke) und gleiche mit Bildern ab. Ein Ort gilt
   erst als erkannt, wenn mindestens zwei unabhängige Merkmale passen.

## Schritt 3: Sicherheit nennen

Sag klar eine von drei Stufen:
- **Sicher** (Name im Bild oder Text, oder zwei Merkmale plus Bestätigung): Ort, Land, Region.
- **Wahrscheinlich** (ein bis zwei Merkmale): nenn die zwei besten Kandidaten und was dafür
  und dagegen spricht.
- **Unklar:** Stell eine gezielte Rückfrage (Wer hat das Reel gepostet? Steht eine Ortsmarke
  da? Kannst du den Anfang des Reels zeigen?). Rate nicht.

Frag, ob der Ort stimmt, bevor du weitermachst.

## Schritt 4: zur fertigen Reise

Steht der Ort fest:
1. Frag Abflughafen, Zeitraum, Personen, Budget.
2. Übergib an `/reise-preise`: Flug und Hotel mit Link, Preis, Quelle, Abrufzeit.
3. Übergib an `/reise-tage`: Tagesroute, die genau den Ort aus dem Reel enthält (der Spot
   aus dem Reel gehört in Tag 1 oder 2, mit Hinweis auf die beste Uhrzeit und Anfahrt).
4. Dazu je ein Satz aus `/reise-einreise` und `/reise-ziel`: Papiere, Wetter im Reisezeitraum.

Am Ende steht eine Übersicht: Ort (mit Sicherheit), Flug, Hotel, Tagesroute, Gesamtkosten
grob, und der Satz: **Gebucht wird nichts, bevor du Ja sagst, und gebucht wird nur von dir.**
Die Reihenfolge fürs Buchen macht `/reise-buchung`.
