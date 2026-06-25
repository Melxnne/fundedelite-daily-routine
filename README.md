# Market Analysis Routine

Tägliche Cloud-Routine: zieht Markt-OHLC-Daten (Gold/US500 via Yahoo Finance),
High-Impact-News (ForexFactory-Feed) und World-News-Headlines (Reuters/BBC RSS),
gleicht das gegen das vollständig ausgefüllte Silver-Bullet-Rulebook (8 Faktoren)
ab und schreibt einen täglichen Report inklusive valider Setup-Bewertung.

**Self-evolving:** Jeder Report hat eine "Routine-Feedback"-Sektion, die Probleme und
Verbesserungsvorschläge dokumentiert. Wiederholte Vorschläge werden eingebaut.

**Komplett kostenlos, kein Login irgendwo.** Kein FundedElite-Account-Zugriff, kein
TradingView-Login, kein MetaApi. Dafür auch: kein Abgleich gegen deine echten
Trades/Positionen – nur reine Markt-/Level-Analyse auf Preisdaten-Basis.

## 1. Repo aufsetzen

```bash
git init
git add .
git commit -m "init"
```

Repo auf GitHub als privat anlegen, dann:

```bash
git remote add origin git@github.com:<dein-user>/market-analysis-routine.git
git push -u origin main
```

## 2. Lokal testen (einmalig)

```bash
cd scripts
pip install -r ../requirements.txt
python fetch_market_data.py
python fetch_economic_calendar.py
```

Output liegt in `data/raw/`. Keine Secrets, kein `.env` zwingend nötig - die Defaults
in `.env.example` funktionieren ohne Anpassung.

## 3. Claude Code Routine einrichten

1. https://claude.ai/code -> Repo verbinden (GitHub App installieren, falls noch
   nicht geschehen).
2. **New Routine** -> Prompt: Inhalt von
   `.claude/routines/daily-market-analysis-routine.md` einfügen.
3. Trigger: Scheduled, täglich, Uhrzeit nach deiner Wahl.
4. **Environment Variables in der Routine:**
   - `YF_DISABLE_CURL_CFFI=1` — verhindert TLS-Fehler via curl_cffi/Proxy (Pflicht)
   - `GITHUB_TOKEN=<dein-PAT>` — Classic PAT mit `repo`-Scope für Push-Rechte
5. Branch-Safety bleibt auf Default (`claude/`-Präfix) - Reports landen als PR.

### GitHub PAT erstellen (für Push-Rechte)
1. https://github.com/settings/tokens -> Generate new token (classic)
2. Scopes: `repo` (Full control of private repositories)
3. Token in der Routine als `GITHUB_TOKEN` Environment Variable eintragen
4. **Nicht in den Code committen** (steht bereits in `.gitignore`)

## 4. Rulebook

`rulebook/silver_bullet_rulebook.md` enthält die 8 vollständig definierten Confluence-Faktoren
(Stand 2026-06-26). Anpassungen an eigene Regeln direkt in der Datei vornehmen.
`rulebook/extended_analysis_notes.md` dokumentiert Erweiterungen und das Self-Evolution-Protokoll.

## Was bewusst fehlt

- **Account-/Trade-Daten (FundedElite/MT5):** würde MetaApi (oder eine vergleichbare
  Cloud-Bridge) brauchen, also laufende Kosten. Wenn du das später doch willst:
  entweder zurück auf MetaApi (Cent-Beträge/Monat bei Deploy/Undeploy pro Lauf) oder
  lokal mit der offiziellen `MetaTrader5`-Python-Lib gegen dein offenes Terminal,
  als Desktop Scheduled Task statt Cloud Routine.
- **Echter TradingView-/FundedElite-Login:** technisch nur über Browser-Automation
  mit deinen Live-Credentials möglich - mache ich nicht (ToS-Risiko, Sicherheits-
  risiko für den Funded-Account, in der Cloud-Routine sowieso kein Browser-Zugriff).

## Datenqualität

Yahoo-Finance-Daten (GC=F, ES=F) sind keine 1:1-Kopie deines Broker-Feeds. Für
Session-Highs/Lows und FVG-Analyse auf 5m/1h-Basis ist die Abweichung in der Praxis
klein, für exakte Tick-Execution-Levels reicht das nicht.

## TradingView Levels (separates Thema)

Für tatsächliches Einzeichnen direkt im Chart: ein Pine Script Indikator, der läuft
dauerhaft in TradingView, unabhängig von dieser Routine. Sag Bescheid, wenn ich den
aufsetzen soll.
