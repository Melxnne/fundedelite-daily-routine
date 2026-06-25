# Daily Market Analysis Routine

Führe folgende Schritte aus, in dieser Reihenfolge:

---

## 0. Umgebung vorbereiten

```bash
pip install -r requirements.txt
```

Setze immer diese Env-Vars **vor** allen Python-Aufrufen:
```bash
export YF_DISABLE_CURL_CFFI=1      # Verhindert TLS-Fehler via curl_cffi/Proxy
export REQUESTS_CA_BUNDLE=""       # Fallback-CA-Bundle deaktivieren wenn nötig
```

**GitHub-Push-Vorbereitung:** Falls `GITHUB_TOKEN` als Umgebungsvariable gesetzt ist,
konfiguriere den Remote einmalig mit Token-Auth:
```bash
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/Melxnne/fundedelite-daily-routine.git"
```
Ohne `GITHUB_TOKEN` ist Push nicht möglich – Report wird dennoch lokal committed, und der
fehlgeschlagene Push wird im Report unter "Technischer Hinweis" dokumentiert.

---

## 1. Daten holen (alle drei parallel starten)

```bash
python scripts/fetch_market_data.py        # Gold + US500, 5m + 1h via Yahoo Finance
python scripts/fetch_economic_calendar.py  # ForexFactory High-Impact Events (24h)
python scripts/fetch_world_news.py         # RSS World-News (Reuters, BBC)
```

Falls ein Script fehlschlägt: Fehler im Report benennen, restliche Analyse mit
verfügbaren Daten trotzdem ausführen.

---

## 2. Daten lesen

Lies alle drei erzeugten JSON-Dateien aus `data/raw/` für das heutige Datum:
- `market_data_<YYYY-MM-DD>.json`
- `economic_calendar_<YYYY-MM-DD>.json`
- `world_news_<YYYY-MM-DD>.json`

Lies außerdem:
- `rulebook/silver_bullet_rulebook.md` (Confluence-Faktoren)
- `rulebook/extended_analysis_notes.md` (Erweiterungen, DXY-Kontext, Self-Evolution)

---

## 3. Report erstellen: `reports/report_<YYYY-MM-DD>.md`

Der Report hat folgende Sektionen:

### 0. Technischer Hinweis (Fetch-Status)
Tabelle: welche Scripts OK / FEHLER, kurze Erklärung bei Fehlern.

### 1. World-News-Snapshot
Lies `world_news_*.json`:
- Wie viele Artikel gesamt, wie viele GOLD-relevant, wie viele EQUITY-relevant?
- World-News-Gate aktiv? (≥3 relevante Artikel)
- Liste der Top-5 relevantesten Headlines (Titel + Quelle + Schlagwörter)
- Kurze Einschätzung: Was bedeutet das für den Handelstag? (Risk-On / Risk-Off / unklar)

### 2. High-Impact-News (Wirtschaftskalender, nächste 24h)
Aus `economic_calendar_*.json`. Jedes High-Impact-Event mit Uhrzeit UTC, Währung, Titel.
Wenn leer: "Kein High-Impact-Event im 24h-Fenster". News-Filter-Status (aktiv / nicht aktiv).

### 3. Session-Highs/Lows (Tagesstruktur, UTC)
Für Gold (GC=F) und US500 (ES=F) je eine Tabelle:
- Asia (00:00–07:59 UTC): High, Low, Candle-Count
- London (08:00–12:59 UTC): High, Low, Candle-Count
- NY (13:00–22:50 UTC): High, Low, Candle-Count
- Letzte 1h-Kerze: OHLC + Zeitstempel
- Auffälligkeiten (Sweeps, Dominanz einer Session)

### 4. HTF-Bias (1h-Struktur)
Für beide Symbole:
- Letzte ≥5 Swing-Highs und Swing-Lows aus `htf_1h`
- HH/HL → Bullish | LH/LL → Bearish | gemischt → Range/Mixed
- Ehrliche Einschätzung: Ist die Struktur eindeutig oder mehrdeutig?

### 5. FVGs und Equal Highs/Lows (5m, letzte ~120 Kerzen)
Für beide Symbole:
- Top-5 FVGs nach Größe, mit Zeitstempel, Typ (bullish/bearish), Top/Bottom/Size
- Equal Highs und Equal Lows (Toleranz 0.05%): aktuelle Liquiditätszonen

### 6. DXY-Kontext (manuell)
Da kein DXY-Script vorhanden: kurze Einschätzung auf Basis der Wochennachrichten
(stärkt/schwächt DXY? Korrelation zu Gold kommentieren). Wenn keine Info verfügbar: "Keine DXY-Daten, übersprungen."

### 7. Confluence-Check gegen Rulebook (nach `rulebook/silver_bullet_rulebook.md`)

Für Gold und US500 je eine Tabelle mit allen 8 Faktoren:

| # | Faktor | Status | Begründung |
|---|---|---|---|
| 1 | HTF-Bias klar | ✅/❌/⚠️ | ... |
| 2 | Liquiditätssweep | ✅/❌/⚠️ | ... |
| 3 | FVG in HTF-Richtung | ✅/❌/⚠️ | ... |
| 4 | Order Block | ✅/❌/⚠️ | ... |
| 5 | MSS auf 5m | ✅/❌/⚠️ | ... |
| 6 | Session-Kontext | ✅(stark)/✅(schwach)/❌ | ... |
| 7 | Premium/Discount | ✅/❌/⚠️ | ... |
| 8 | Sauberer Weg zum Ziel | ✅/❌/⚠️ | ... |
| **Hard Gate** | News-Filter | ✅ frei / ❌ blockiert | ... |
| **Hard Gate** | World-News-Gate | ✅ frei / ❌ aktiv | ... |

Score: X/8. Schwelle: ≥5 für Setup.

### 8. Setup-Sektion

**Nur wenn:** Score ≥5/8 UND beide Hard Gates frei UND HTF-Bias eindeutig.

Für jedes valide Setup das Template aus `silver_bullet_rulebook.md` ausfüllen:
- Symbol, Richtung, HTF-Bias
- Faktor-Score mit Detailliste
- Entry-Zone (FVG-Range), Stop-Loss, Take-Profit
- Qualitäts-Hinweis (knapp erfüllte Faktoren explizit benennen)

**Wenn Schwelle nicht erreicht:** "Kein Setup nach Rulebook – fehlende Faktoren: [Liste]"

Sei ehrlich. Wenn ein Faktor knapp oder zweideutig erfüllt ist: als ⚠️ markieren,
nicht als ✅ glattzubügeln. Die Setup-Sektion ist Regelanwendung, keine Empfehlung.

### 9. Fazit

Kompakte Tabelle: Symbol | HTF-Bias | Letzte Notiz | News-Gate | World-News-Gate | Setup?

Relevante Levels für den nächsten Handelstag (Support/Resistance, FVG-Cluster, EQL).

### 10. Routine-Feedback (Self-Evolution)

Diese Sektion ist für die Routine selbst, nicht für den Trader. Bitte nach diesem Schema:

```
**Was hat geklappt:**
- [Script / Analyse-Teil]: OK

**Was hat nicht geklappt / Probleme:**
- [Script / Analyse-Teil]: [Fehler / Problem]

**Verbesserungsvorschläge für nächste Ausführung:**
1. [Konkreter Vorschlag]
2. [Konkreter Vorschlag]

**Rulebook-Qualitäts-Hinweis:**
[Waren die Faktoren klar genug definiert? Was war mehrdeutig?]
```

Diese Sektion wird in `rulebook/extended_analysis_notes.md` (Protokoll-Tabelle)
als nächster Eintrag aufgenommen, sobald ein Vorschlag ≥2x erscheint.

---

## 4. Commit und Push

```bash
# Report committen
git add reports/report_<YYYY-MM-DD>.md
git commit -m "report: daily market analysis <YYYY-MM-DD>"

# Push auf Branch mit Präfix claude/
BRANCH="claude/report-<YYYY-MM-DD>"
git checkout -b "$BRANCH"
git push -u origin "$BRANCH"
```

Falls Push fehlschlägt (kein `GITHUB_TOKEN` oder 403):
- Im Report unter Sektion 0 dokumentieren
- Commit bleibt lokal erhalten
- Kein PR öffnen ohne erfolgreichen Push

Falls Push erfolgreich:
```bash
gh pr create \
  --title "Daily Analysis <YYYY-MM-DD>" \
  --body "Automatisch generierter Report. Setup-Score und World-News-Status im Report." \
  --base master \
  --head "$BRANCH"
```

---

## Allgemeine Grundsätze

- **Ehrlichkeit:** Keine Beschönigung. Fehlende Daten = explizit benennen.
- **Kein Account-Zugriff:** Dieser Report ist reine Marktstruktur-Analyse auf Yahoo-Finance-Basis,
  kein Abgleich gegen echte Positionen.
- **Kein Setup erzwingen:** Wenn die Schwelle nicht erreicht wird, ist "kein Setup" das korrekte Ergebnis.
- **Self-Evolution:** Die Routine soll sich weiterentwickeln. Sektion 10 ist Pflicht, nicht optional.
  Wenn dieselbe Verbesserung 2x im Protokoll erscheint, wird sie eingebaut.
