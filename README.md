# FundedElite Daily Routine

Tägliche Cloud-Routine: zieht Account-Snapshot + Trade-History (MT5/FundedElite via
MetaApi) und High-Impact-News (ForexFactory-Feed), gleicht das gegen das Silver-Bullet-
Rulebook ab und schreibt einen Report.

**Kein TradingView-Login/-Scraping.** Levels einzeichnen geht nur über einen Pine
Script Indikator direkt in TradingView, nicht über diese Routine (siehe unten).

## 1. Repo aufsetzen

```bash
git init
git add .
git commit -m "init"
```

Repo auf GitHub als **privat** anlegen, dann:

```bash
git remote add origin git@github.com:<dein-user>/fundedelite-daily-routine.git
git push -u origin main
```

## 2. MetaApi Account anlegen (einmalig, via Web UI)

1. Account auf https://app.metaapi.cloud erstellen.
2. **Provisioning Profile**: Broker-Server-Datei (`.srv`) oder Server-Name hinterlegen
   – Server-Name steht in deinem MT5-Terminal unter Konto-Eigenschaften (z.B.
   `FundedElite-Live01`).
3. **Trading Account** hinzufügen: MT5-Login + **Investor-Passwort** (nicht das
   Trading-Passwort – Investor-PW reicht für Read-Only, ist vorzuziehen).
4. Account deployen, Status `DEPLOYED` abwarten.
5. Token holen: https://app.metaapi.cloud/token → `METAAPI_TOKEN`.
6. Account-ID holen: https://app.metaapi.cloud/accounts → `METAAPI_ACCOUNT_ID`
   (das ist die MetaApi-interne UUID, nicht dein MT5-Login).

Prüfen, ob FundedElite Read-Only-API-Zugriff über einen Drittanbieter überhaupt
erlaubt (ToU) – reines Auslesen ist bei den meisten Prop-Firms unkritisch, aber nicht
überall explizit geregelt.

## 3. Lokal testen (einmalig, bevor die Routine läuft)

```bash
cd scripts
pip install -r ../requirements.txt
cp ../.env.example ../.env
# .env mit METAAPI_TOKEN / METAAPI_ACCOUNT_ID füllen
python fetch_account_snapshot.py
python fetch_trade_history.py
python fetch_economic_calendar.py
```

Output liegt in `data/raw/`. Erst wenn das lokal saubere JSONs liefert, weiter zu
Schritt 4.

## 4. Claude Code Routine einrichten

1. https://claude.ai/code → Repo verbinden (GitHub App installieren, falls noch
   nicht geschehen).
2. **New Routine** → Prompt: Inhalt von
   `.claude/routines/daily-market-account-routine.md` einfügen.
3. Trigger: Scheduled, täglich, Uhrzeit nach deiner Wahl (z.B. nach NY-Close).
4. Secrets/Env-Vars für die Routine setzen: `METAAPI_TOKEN`, `METAAPI_ACCOUNT_ID`
   – über die Secrets-Verwaltung der Routine-Konfiguration in der UI, **nicht** im
   Repo committen. (Stand der UI kann sich ändern, Routines sind aktuell Research
   Preview – im Zweifel in der Claude Code Doku nachsehen.)
5. Branch-Safety bleibt auf Default (`claude/`-Präfix) – Reports landen als PR, kein
   Direct-Push auf main.

## 5. Rulebook befüllen

`rulebook/silver_bullet_rulebook.md` ist nur ein Platzhalter mit den 8 Slots und dem
News-Filter-Hinweis. Aktuellen Stand deines Regelwerks reinkopieren, sonst kann die
Routine Trades nicht sinnvoll abgleichen.

## TradingView Levels (separates Thema)

Da es nur ums Einzeichnen geht: ein Pine Script Indikator, der die Levels selbst
berechnet (z.B. Session-High/Low, FVGs, Order Blocks) und direkt im Chart zeichnet,
läuft dauerhaft in TradingView – kein externer Trigger, kein Login-Problem. Sag
Bescheid, wenn ich den jetzt aufsetzen soll.
