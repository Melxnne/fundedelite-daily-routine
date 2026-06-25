# Silver Bullet Rulebook (ICT/SMC) – XAUUSD / US500

Version: 2026-06-26 | Erster vollständiger Stand

---

## Mandatory Pre-Entry Filter (Hard Gate – kein Confluence-Faktor)

Vor jedem Setup prüfen:
- **News-Filter:** `data/raw/economic_calendar_*.json` auf High-Impact-Events für USD oder XAU
  im Fenster ±30 min um den geplanten Entry prüfen. Bei Treffer: kein Entry.
- **World-News-Context:** `data/raw/world_news_*.json` auf geopolitische Schocks, Fed-Statements
  oder Krisen-Headlines prüfen. Wenn ein direkter Marktbezug erkennbar ist (Eskalation, Sanktionen,
  Zentralbank-Überraschung), Entry verkleinern oder streichen.

---

## Confluence-Faktoren (min. 5 von 8 erforderlich für ein Setup)

### 1. HTF-Bias klar (1h-Struktur)
**Erfüllt:** 1h-Chart zeigt klares HH + HL (bullish) oder LH + LL (bearish) über die letzten
≥3 Swing-Punkte. Kein Mixed/Range-Bild.
**Nicht erfüllt:** Struktur ist Mixed (LH + HL), Range oder nach einem starken News-Spike zerrissen.
**Quelle:** `htf_1h` in `market_data_*.json`, Swing-Analyse.

---

### 2. Liquiditätssweep vor Entry
**Erfüllt:** Preis hat unmittelbar vor dem Setup-Fenster eine Liquiditätszone genommen:
Equal Highs/Lows (EQL) auf 5m, Previous Session High/Low (Asia-High/Low, London-High/Low),
oder das Tages-High/Low (PDH/PDL). Der Sweep endet mit einem Rejection-Close (Wick ohne Schlusskurs
jenseits der Zone).
**Nicht erfüllt:** Kein erkennbarer Sweep; Preis läuft einfach weiter ohne vorherige Liquidity-Abholung.
**Quelle:** Equal Highs/Lows-Sektion im Report, Session-Highs/Lows.

---

### 3. FVG (Fair Value Gap) auf dem Entry-TF (5m) in HTF-Richtung
**Erfüllt:** Ein FVG auf dem 5m-Chart in Richtung des HTF-Bias existiert und ist noch offen
(wurde nicht vollständig gefüllt). Mindestgröße: ≥1.00 Punkte (Gold) / ≥2.0 Punkte (US500).
**Nicht erfüllt:** Kein relevantes FVG in Richtung des Bias, oder es wurde bereits vollständig
geschlossen.
**Quelle:** FVG-Sektion im Report.

---

### 4. Order Block (OB) als Preisanker
**Erfüllt:** Ein bullisher oder bearisher OB liegt in der FVG-Zone oder direkt darunter/darüber.
Bullisher OB = letzte bearishe Kerze vor einem starken bullishen Impuls (Körper zählt).
Bearisher OB = letzte bullishe Kerze vor einem starken bearishen Impuls.
**Einfacher Proxy (aus reinen OHLCV-Daten ableitbar):** Die Kerze unmittelbar vor dem Impuls,
der die FVG erzeugt hat, gilt als OB. Liegt der aktuelle Preis in diesem Körper? → Erfüllt.
**Nicht erfüllt:** Entry liegt weit vom OB entfernt, kein klar definierbarer OB-Körper.
**Quelle:** OHLCV-Daten um die FVG-erzeugenden Kerzen.

---

### 5. Market Structure Shift (MSS) auf 5m nach dem Sweep
**Erfüllt:** Nach dem Liquiditätssweep schließt eine 5m-Kerze über (Long) / unter (Short)
das unmittelbar vorangehende Swing-High/Low → bestätigt den Richtungswechsel auf dem Entry-TF.
Der MSS markiert den frühestmöglichen Entry-Zeitpunkt.
**Nicht erfüllt:** Preis dreht zwar, aber kein sauberer Swing-Break auf Schlussbasis.
**Quelle:** 5m-OHLCV, letzter Swing-High/Low vor dem potenziellen Entry.

---

### 6. Session-Kontext-Filter (Ersatz für alten Killzone-Zwang)
**Erfüllt (stark):** Entry liegt in einem Silver-Bullet-Fenster:
  - Asia Silver Bullet: 02:00–03:00 UTC
  - London Silver Bullet: 09:00–10:00 UTC
  - NY AM Silver Bullet: 14:00–15:00 UTC (10–11 Uhr New York)
  - NY Lunch Silver Bullet: 18:00–19:00 UTC (14–15 Uhr New York)
**Erfüllt (schwach, zählt aber):** Entry liegt zumindest in einer aktiven Session
(London 07:00–12:00 UTC oder NY 13:00–21:00 UTC).
**Nicht erfüllt:** Asia-Drift, Sonntag-Open, oder kurz nach einem großen News-Spike (< 15 min).
**Hinweis:** Dieser Faktor ist der einzige, der in zwei Stärke-Stufen erfüllt sein kann.
Starke Erfüllung zählt 1, schwache Erfüllung zählt 0.5 (aufrunden auf 1 wenn ≥4 andere erfüllt).

---

### 7. Premium/Discount-Kontext des Entries
**Erfüllt:** Bei Long-Setups liegt der Entry in der unteren Hälfte (Discount) der aktuellen
HTF-Range (Asia-Range oder Tages-Range). Bei Short-Setups in der oberen Hälfte (Premium).
**Berechnung:** Equilibrium = (Range-High + Range-Low) / 2. Long-Entry < EQ = Discount = erfüllt.
Short-Entry > EQ = Premium = erfüllt.
**Nicht erfüllt:** Longeinstieg im Premium oder Shorteinstieg im Discount (gegen die Statistik).
**Ausnahme:** Bei Continuation-Trades nach einem klaren Breakout kann dieser Faktor überbrückt
werden, aber dann müssen die anderen 7 Faktoren deutlich erfüllt sein (≥6/8).
**Quelle:** Session-Highs/Lows aus dem Report.

---

### 8. Sauberer Weg zum Ziel (keine direkte Blockade)
**Erfüllt:** Zwischen Entry-Zone und der Ziel-Liquidität (nächstes Session-High/Low,
EQL, offenes FVG auf höherem TF) liegt keine relevante Widerstandszone (kein offenes
bearishes FVG bei Longs, kein OB des Gegners direkt dazwischen).
**Prüfung:** Im Report die FVG-Liste und Session-Levels als Hindernisse durchgehen.
**Nicht erfüllt:** Ein signifikantes gegenläufiges FVG oder Session-Level liegt zwischen
Entry und Ziel – das verkürzt den Weg und verschlechtert das R:R.
**Quelle:** FVG-Sektion + Session-Level-Sektion im Report.

---

## Setup-Template (bei ≥5/8 erfüllt + News-Filter frei)

```
Symbol:          [XAUUSD / US500]
Richtung:        [Long / Short]
HTF-Bias:        [Bullish / Bearish] – basierend auf 1h-Struktur
Faktor-Score:    X/8 (Faktoren Y, Z, ... erfüllt; Faktor A, B, ... nicht erfüllt)

Entry-Zone:      [FVG-Bottom – FVG-Top] bzw. OB-Körper
Stop-Loss:       [Unterhalb des Sweeps / Oberhalb des OB] – kein fester Pip-Wert
Take-Profit:     [Nächste Liquiditätszone: EQL / Session-High-Low]

Qualitäts-Hinweis:
  Knapp erfüllte Faktoren: [...]
  Risiko-Faktoren: [...]
```

---

## Notizen / Änderungshistorie

- 2026-06-25: Rulebook war leerer Platzhalter, kein valider Score möglich.
- 2026-06-26: Erste vollständige Version mit 8 definierten Faktoren.
  Killzone-Zeitfenster bleibt loser Faktor (Nr. 6) mit schwacher/starker Erfüllung.
  News-Filter bleibt Hard Gate (außerhalb der 8er-Zählung).
  World-News-Context als zweites Hard-Gate ergänzt.
