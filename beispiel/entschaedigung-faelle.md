# Drei Beispielfälle für reise-entschaedigung

```bash
# 1. Technischer Defekt, 4 Stunden zu spät: 400 Euro (über 1.500 km innerhalb der EU)
python3 skills/reise-entschaedigung/anspruch.py --von MUC --nach LIS --verspaetung 4 --grund technisch

# 2. Annulliert, 3 Tage vorher, Grund liegt bei der Airline: 600 Euro (über 3.500 km)
python3 skills/reise-entschaedigung/anspruch.py --von FRA --nach JFK --art annullierung --vorwarnung-tage 3 --grund airline

# 3. Unwetter, 5 Stunden zu spät: kein Anspruch (außergewöhnlicher Umstand)
python3 skills/reise-entschaedigung/anspruch.py --von VIE --nach PMI --verspaetung 5 --grund wetter
```

Mit `--antrag antrag.txt --name "Max Muster" --airline Lufthansa --flugnr LH400 --datum 2026-10-02` schreibt das Werkzeug den fertigen Antrag.
