#!/usr/bin/env python3
"""Standbilder aus einem Reel oder Video ziehen, damit Claude den Ort erkennen kann.

Quelle: eine Videodatei oder ein öffentlicher Link (braucht yt-dlp). Bilder zieht ffmpeg.
Kein Login, keine Cookies. Klappt der Link nicht, mach einen Screenshot.

    python3 frames.py reel.mp4 --anzahl 6 --out frames
    python3 frames.py https://www.instagram.com/reel/XXXX/ --anzahl 6 --out frames
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


def laenge(datei):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", datei],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quelle")
    ap.add_argument("--anzahl", type=int, default=6)
    ap.add_argument("--out", default="frames")
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg fehlt. Installieren (zum Beispiel winget install ffmpeg) oder einen Screenshot nutzen.")
    quelle = a.quelle
    tmp = None
    if quelle.startswith("http"):
        if not shutil.which("yt-dlp"):
            sys.exit("yt-dlp fehlt. Installieren (pip install yt-dlp) oder einen Screenshot nutzen.")
        tmp = tempfile.mkdtemp(prefix="reel-")
        r = subprocess.run(["yt-dlp", "-o", os.path.join(tmp, "v.%(ext)s"), "--no-playlist", "--no-cookies", quelle],
                           capture_output=True, text=True)
        dateien = glob.glob(os.path.join(tmp, "v.*"))
        if r.returncode != 0 or not dateien:
            print("Der Link ließ sich ohne Anmeldung nicht laden. Mach stattdessen einen Screenshot oder speichere das Video.")
            print(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "")
            sys.exit(2)
        quelle = dateien[0]
    if not os.path.exists(quelle):
        sys.exit(f"Datei nicht gefunden: {quelle}")
    dauer = laenge(quelle)
    if dauer <= 0:
        sys.exit("Länge des Videos nicht lesbar.")
    os.makedirs(a.out, exist_ok=True)
    n = max(1, a.anzahl)
    for i in range(n):
        t = dauer * (i + 0.5) / n
        ziel = os.path.join(a.out, f"bild-{i + 1:02d}.jpg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", quelle, "-frames:v", "1",
                        "-vf", "scale=720:-2", "-q:v", "3", ziel], check=True)
        print(f"{ziel}  (bei {t:.1f} s von {dauer:.1f} s)")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    print("Fertig. Öffne die Bilder, achte auf Schilder, Schriftzüge, Wahrzeichen, Küstenlinie, Architektur.")


if __name__ == "__main__":
    main()
