# Daily Market & Account Routine

Führe folgende Schritte aus, in dieser Reihenfolge:

1. `pip install -r requirements.txt` (falls Dependencies fehlen).
2. `python scripts/fetch_account_snapshot.py`
3. `python scripts/fetch_trade_history.py`
4. `python scripts/fetch_economic_calendar.py`
5. Lies die drei erzeugten JSON-Dateien aus `data/raw/` für das heutige Datum.
6. Lies `rulebook/silver_bullet_rulebook.md`.
7. Erstelle `reports/report_<YYYY-MM-DD>.md` mit:
   - Account-Snapshot: Equity, Balance, offene Positionen (Symbol, Richtung, Größe,
     aktueller P/L).
   - Geschlossene Trades der letzten 24h: pro Trade kurz, ob er laut Rulebook
     mindestens 5 von 8 Confluence-Faktoren erfüllt hätte (so weit aus den Daten
     ableitbar) und ob der News-Filter zum Entry-Zeitpunkt verletzt wurde.
   - High-Impact-News der nächsten 24h aus `economic_calendar_*.json`, mit
     Uhrzeit (UTC) – das ist der Pflicht-Filter für morgige Setups.
   - Kurzes Fazit: Auffälligkeiten, Regelverstöße, offene Risiken.
8. Sei ehrlich und direkt bei Regelverstößen, nicht beschönigen (siehe
   Trading-Honesty-Vorgabe). Keine Trade-Empfehlungen, nur Analyse der bestehenden
   Lage gegen das Rulebook.
9. Committe `reports/report_<YYYY-MM-DD>.md` auf einen Branch mit Präfix `claude/`
   und öffne einen PR (Branch-Safety-Default der Routine).

Falls eine der drei Fetch-Scripts mit Fehler abbricht (z.B. MetaApi-Token ungültig,
Account nicht deployed): Fehler im Report klar benennen, restliche Schritte trotzdem
mit den verfügbaren Daten ausführen.
