# Daily Market Analysis Routine

Führe folgende Schritte aus, in dieser Reihenfolge:

1. `pip install -r requirements.txt` (falls Dependencies fehlen).
2. `python scripts/fetch_market_data.py`
3. `python scripts/fetch_economic_calendar.py`
4. Lies die zwei erzeugten JSON-Dateien aus `data/raw/` für das heutige Datum.
5. Lies `rulebook/silver_bullet_rulebook.md`.
6. Erstelle `reports/report_<YYYY-MM-DD>.md` mit:
   - Gold (GC=F) und US500 (ES=F): aktuelle Session-Highs/Lows (Asia/London/NY,
     anhand der UTC-Zeitstempel aus den 5m-Candles ableiten), erkennbare FVGs/Equal
     Highs-Lows auf dem 5m-Chart, HTF-Bias aus den 1h-Candles.
   - Abgleich gegen die Confluence-Faktoren im Rulebook: welche der 8 Faktoren sind
     aktuell erkennbar erfüllt (so weit aus reinen Preisdaten ableitbar, kein
     Orderflow/Volumen-Profil enthalten).
   - High-Impact-News der nächsten 24h aus `economic_calendar_*.json` – Pflicht-Filter
     für heutige/morgige Setups.
   - Kurzes Fazit: Bias, relevante Levels, ob der News-Filter aktuell greift.
7. Sei ehrlich und direkt, keine Beschönigung (siehe Trading-Honesty-Vorgabe). Das
   ist eine Markt-Analyse auf Basis von Yahoo-Finance-Daten, **kein** Abgleich gegen
   echte Positionen oder Trades (kein Account-Zugriff in dieser Routine) - das im
   Report auch so benennen, nicht so tun als wäre es dein Live-Account.
8. Committe `reports/report_<YYYY-MM-DD>.md` auf einen Branch mit Präfix `claude/`
   und öffne einen PR (Branch-Safety-Default der Routine).

Falls eines der beiden Fetch-Scripts fehlschlägt: Fehler im Report klar benennen,
restliche Schritte trotzdem mit den verfügbaren Daten ausführen.
