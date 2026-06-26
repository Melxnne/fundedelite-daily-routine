# Extended Analysis Framework – Erweiterungen zum Silver Bullet Rulebook

Diese Datei dokumentiert Analyse-Erweiterungen, die über das Kern-Rulebook hinausgehen.
Sie ergänzt `silver_bullet_rulebook.md`, überschreibt es nicht. Änderungsvorschläge aus der
Routine selbst werden hier gesammelt (Self-Evolution-Protokoll).

---

## A. World-News-Kontext (Makro- und Geopolitik)

### Warum World-News?
Ein Trader öffnet morgens nicht nur den Wirtschaftskalender – er checkt Reuters, Bloomberg und
BBC, weil ein Drohnenangriff auf saudische Ölinfrastruktur oder ein Fed-Kommentar außerhalb
des regulären Kalenders Gold in 10 Minuten um $30 bewegt. Die Routine holt deshalb täglich
einen World-News-Snapshot und filtert auf marktrelevante Schlagwörter.

### Quellen (RSS, kein API-Key nötig)
| Feed | Fokus |
|---|---|
| Reuters Business | Makro, Unternehmens-News |
| Reuters World | Geopolitik, Konflikte |
| BBC Business | Breites Publikum, UK-Perspektive |
| Investing.com Gold RSS | Goldspezifisch |

### Relevanz-Filter (Schlagwörter → Marktbezug)
Die Routine bewertet jeden Artikel auf Schlagwörter und klassifiziert:

**Gold-relevant (Typ "RISK"):**
- Konflikt: `war`, `attack`, `strike`, `invasion`, `sanction`, `military`, `missiles`
- Fed/Geldpolitik: `federal reserve`, `fed`, `rate`, `interest rate`, `inflation`, `cpi`, `ppi`
- Dollar: `dollar`, `dxy`, `usd`, `treasury`, `yield`
- Rohstoffe: `gold`, `silver`, `oil`, `crude`, `opec`
- Krisen: `recession`, `default`, `banking`, `collapse`, `crisis`

**US500-relevant (Typ "EQUITY"):**
- Earnings, Tech: `earnings`, `revenue`, `nasdaq`, `s&p`, `dow`, `apple`, `nvidia`, `tesla`
- Makro: `gdp`, `unemployment`, `jobs`, `nfp`, `retail sales`
- Politik: `tariff`, `trade war`, `debt ceiling`, `budget`

### Interpretation im Report
- 0 relevante Schlagwörter → normaler Handelstag, kein Zusatzkommentar nötig
- 1-2 relevante Artikel → kurze Erwähnung im Report, kein Gate
- ≥3 relevante Artikel mit direktem Marktbezug → World-News-Gate aktiv, Setup-Kommentar
  mit Hinweis auf erhöhte Volatilitätsgefahr

---

## B. DXY-Kontext (US Dollar Index)

Gold und DXY laufen invers. Wenn die Routine bearishen DXY-Bias erkennt, stärkt das einen
bullishen Gold-Bias – und umgekehrt. Sobald ein DXY-Ticker zuverlässig via yfinance
verfügbar ist (`DX-Y.NYB`), sollte er als dritter Datenstrom aufgenommen werden.

**Status:** Noch nicht implementiert. Nächste Evolution wenn DXY-Daten stabil.

---

## C. Self-Evolution-Protokoll

Die Routine schreibt am Ende jedes Reports eine "Routine-Feedback"-Sektion. Diese dokumentiert:
1. Was hat geklappt (Daten vollständig, Scripts fehlerfrei)?
2. Was hat nicht geklappt (Fehler, fehlende Daten, ungültige Scores)?
3. Offene Fragen / Verbesserungsvorschläge für das nächste Mal

Diese Sektion ist der Rohstoff für Updates an dieser Datei. Wenn die Routine wiederholt
denselben Vorschlag macht, ist das ein Signal, die Änderung tatsächlich einzubauen.

### Protokoll-Einträge

| Datum | Problem | Vorschlag | Status |
|---|---|---|---|
| 2026-06-25 | `curl_cffi` TLS-Fehler via Proxy | `YF_DISABLE_CURL_CFFI=1` permanent setzen | ✅ Umgesetzt |
| 2026-06-25 | Rulebook leer, kein valider Score | 8 Faktoren definieren | ✅ Umgesetzt |
| 2026-06-25 | Kein World-News-Context | RSS-Script `fetch_world_news.py` erstellen | ✅ Umgesetzt |
| 2026-06-25 | Push 403 (kein Token) | `GITHUB_TOKEN` in Routine-Env + Remote-URL-Patch | ✅ Umgesetzt |
| 2026-06-25 | Nur ForexFactory-Kalender, keine Weltnachrichten | Extended Analysis Framework | ✅ Umgesetzt |
| 2026-06-26 | `matched_keywords` leer – Gate-Signal unzuverlässig | Keyword-Matching-Bug in `fetch_world_news.py` beheben | 1x – offen |
| 2026-06-26 | Reuters/AP via Proxy nicht erreichbar | Alternative Feeds (Guardian, AP Atom) als Fallback einrichten | 1x – offen |
| 2026-06-26 | JSON-Key `fvgs_top5` vs. Log "5 FVGs" – inkonsistent | Key zu `fvgs` umbenennen oder Log anpassen | 1x – offen |
| 2026-06-26 | Faktor 4 (OB) und Faktor 5 (MSS) nicht automatisch berechenbar | OB- und Swing-Break-Erkennung in `analyze_market_data.py` ergänzen | 1x – offen |
| 2026-06-26 | Wochentags-Flag fehlt im Report | Freitag-Hinweis als automatischen Flag implementieren (D.2) | 1x – offen |

---

## D. Tradeable-Setup-Erweiterungen (zukünftig)

Diese Erweiterungen sind dokumentiert, aber noch nicht implementiert. Einbau wenn Datenbasis
stabil und Rulebook mindestens 2 Wochen Live-getestet.

### D.1 Relative Strength (Gold vs. US500 Korrelation)
Wenn Gold steigt und US500 fällt → Risk-Off-Kontext → stärkt Gold-Long, schwächt US500-Long.
Routine kann diesen Kontext aus den beiden HTF-Bias-Wertungen ableiten (keine Extra-Daten nötig).

### D.2 Wochentags-Filter
ICT betont, dass Montag oft Setup-Vorbereitung ist und Dienstag-Donnerstag die besten
Entry-Tage sind. Freitag = Profit-Taking-Session. Routine sollte Setup-Score kommentieren,
wenn Wochentag sub-optimal.

### D.3 Historische Report-Auswertung
Wenn ≥5 Reports vorhanden, rückblickend prüfen: Wie oft war ein gesignaltes Setup profitabel?
→ gibt Rulebook-Qualität Feedback. Implementierbar per Python-Script das alle
`reports/*.md`-Dateien nach Setup-Sektionen durchsucht.
