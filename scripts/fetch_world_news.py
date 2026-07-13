"""Holt World-News-Headlines via RSS (kein API-Key, kein Login).

Mehrere Feeds: Reuters Business/World, BBC Business. Filtert auf marktrelevante
Schlagwörter (Gold, Fed, Geopolitik, Equities) und klassifiziert in GOLD-relevant
und EQUITY-relevant. Output ist eine JSON-Datei für den täglichen Report.

Einschränkung: RSS-Feeds zeigen nur die letzten ~20-50 Artikel; kein Volltext,
nur Titel + Beschreibung. Für Trend-Analyse reicht das; für tiefe Interpretation
muss der Trader den Artikel selbst lesen.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from config import DATA_RAW_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_world_news")

RSS_FEEDS = [
    {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews"},
    {"name": "Reuters World",    "url": "https://feeds.reuters.com/reuters/worldNews"},
    {"name": "BBC Business",     "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"name": "Investing Gold",   "url": "https://www.investing.com/rss/news_25.rss"},
    # Additional sources (redundancy for when Reuters 502s via proxy tunnel)
    {"name": "AP Business",     "url": "https://feeds.apnews.com/rss/apf-business"},
    {"name": "Al Jazeera",      "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    # Fallback-Feeds: Reuters/AP werden über den Proxy wiederholt mit 502 (Tunnel-Fehler)
    # blockiert (seit 26. Juni mehrfach dokumentiert, siehe extended_analysis_notes.md).
    # MarketWatch/CNBC laufen über denselben Proxy zuverlässig durch.
    {"name": "MarketWatch",     "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
    {"name": "CNBC",            "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
]

# Schlagwörter → Marktrelevanz-Kategorie
# Hinweis: Matching erfolgt mit Wortgrenzen (siehe _compile_keyword_pattern), nicht als
# naiver Substring-Check. Frühere Version matchte z.B. "war" in "warns" und "ppi" in
# "shopping", was zu False Positives führte (mehrfach dokumentiert in
# extended_analysis_notes.md). Bare "gold"/"silver" wurden durch spezifischere Phrasen
# ersetzt, da sie sonst auch metaphorische Verwendungen treffen (z.B. "blue gold" für
# Agavenschnaps).
GOLD_KEYWORDS = {
    "war", "attack", "strike", "invasion", "sanction", "military", "missile", "missiles",
    "federal reserve", "fed", "rate hike", "rate cut", "interest rate", "inflation",
    "cpi", "ppi", "core inflation", "dollar", "dxy", "usd", "treasury", "yield",
    "gold price", "gold prices", "gold futures", "spot gold", "xau", "silver price",
    "opec", "oil", "crude", "bullion", "safe haven",
    "recession", "default", "banking crisis", "collapse", "crisis", "geopolit",
    "ukraine", "russia", "iran", "middle east", "china tariff",
}

EQUITY_KEYWORDS = {
    "earnings", "revenue", "nasdaq", "s&p", "s&p 500", "dow jones", "dow ",
    "apple", "nvidia", "tesla", "meta", "alphabet", "amazon", "microsoft",
    "gdp", "unemployment", "jobs", "nfp", "payroll", "retail sales",
    "tariff", "trade war", "debt ceiling", "budget", "deficit",
    "ipo", "merger", "acquisition", "layoffs", "buyback",
}


def _fetch_rss(url: str, name: str) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; daily-routine-bot/1.0)"}
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=15) as resp:
            content = resp.read()
        root = ET.fromstring(content)
    except Exception as exc:
        logger.warning("RSS-Fetch fehlgeschlagen [%s]: %s", name, exc)
        return []

    items = []
    # Both Atom and RSS2
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        desc  = (item.findtext("description") or "").strip()
        link  = (item.findtext("link") or "").strip()
        pub   = (item.findtext("pubDate") or "").strip()
        items.append({"source": name, "title": title, "description": desc,
                      "link": link, "pub_date": pub})
    return items


def _compile_keyword_pattern(keywords: set[str]) -> re.Pattern:
    """Baut ein Wortgrenzen-Pattern statt naivem Substring-Match.

    `\\b` allein reicht nicht für Phrasen mit Sonderzeichen wie "s&p", daher
    Lookaround auf Nicht-Alphanumerisch davor/danach.
    """
    # Optionales "s"/"es"-Suffix erlaubt Pluralformen (z.B. "strikes", "sanctions"),
    # ohne die Wortgrenzen-Prüfung selbst aufzuweichen.
    alt = "|".join(
        re.escape(kw) + r"(?:es|s)?" for kw in sorted(keywords, key=len, reverse=True)
    )
    return re.compile(rf"(?<![a-z0-9])(?:{alt})(?![a-z0-9])", re.IGNORECASE)


GOLD_PATTERN = _compile_keyword_pattern(GOLD_KEYWORDS)
EQUITY_PATTERN = _compile_keyword_pattern(EQUITY_KEYWORDS)


def _classify(title: str, desc: str) -> list[str]:
    text = (title + " " + desc).lower()
    tags = []
    if GOLD_PATTERN.search(text):
        tags.append("GOLD")
    if EQUITY_PATTERN.search(text):
        tags.append("EQUITY")
    return tags


def fetch_news() -> dict:
    now = datetime.now(timezone.utc)
    all_items: list[dict] = []

    for feed in RSS_FEEDS:
        raw = _fetch_rss(feed["url"], feed["name"])
        logger.info("%s: %d Artikel geladen", feed["name"], len(raw))
        all_items.extend(raw)

    classified: list[dict] = []
    for item in all_items:
        tags = _classify(item["title"], item["description"])
        classified.append({
            "source":      item["source"],
            "title":       item["title"],
            "pub_date":    item["pub_date"],
            "tags":        tags,
            "link":        item["link"],
            "description": item["description"][:300] if item["description"] else "",
        })

    relevant = [a for a in classified if a["tags"]]
    gold_articles    = [a for a in relevant if "GOLD"   in a["tags"]]
    equity_articles  = [a for a in relevant if "EQUITY" in a["tags"]]

    # Aktiviere World-News-Gate wenn ≥3 relevante Artikel
    gate_active = len(relevant) >= 3

    return {
        "fetched_at":           now.isoformat(),
        "total_articles":       len(all_items),
        "relevant_count":       len(relevant),
        "gold_relevant_count":  len(gold_articles),
        "equity_relevant_count": len(equity_articles),
        "world_news_gate_active": gate_active,
        "gold_articles":        gold_articles[:10],
        "equity_articles":      equity_articles[:10],
        "all_relevant":         relevant[:20],
    }


def main() -> None:
    result = fetch_news()
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = DATA_RAW_DIR / f"world_news_{date_str}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(
        "%d Artikel total, %d relevant (GOLD: %d, EQUITY: %d), Gate=%s -> %s",
        result["total_articles"],
        result["relevant_count"],
        result["gold_relevant_count"],
        result["equity_relevant_count"],
        result["world_news_gate_active"],
        out_path,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("World-News-Fetch fehlgeschlagen")
        sys.exit(1)
