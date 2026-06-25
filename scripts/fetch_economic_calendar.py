"""Holt den Wochen-Kalender (ForexFactory JSON-Feed, kein Login nötig) und filtert
High-Impact-Events im Lookahead-Fenster (Default 24h). Deckt den Pflicht-News-Filter
aus dem Silver-Bullet-Rulebook ab.

Hinweis: Der Feed-Endpoint von ForexFactory/Fair Economy ändert sich gelegentlich
(historisch: ff_calendar_thisweek.json bzw. cdn-nfs.faireconomy.media). URL ist über
ECONOMIC_CALENDAR_URL konfigurierbar, falls sich das wieder ändert. Rate-Limit beachten:
laut Community max. 2 Requests / 5 Minuten pro IP -> für 1x täglich unkritisch.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from dateutil import parser as date_parser

from config import DATA_RAW_DIR, load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_economic_calendar")

LOOKAHEAD_HOURS = int(os.getenv("NEWS_FILTER_LOOKAHEAD_HOURS", "24"))
RELEVANT_CURRENCIES = {
    c.strip().upper()
    for c in os.getenv("NEWS_FILTER_CURRENCIES", "USD,XAU").split(",")
    if c.strip()
}


def _parse_event_time(raw_date: str) -> datetime | None:
    try:
        parsed = date_parser.parse(raw_date)
    except (ValueError, TypeError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def fetch_calendar() -> dict:
    settings = load_settings()
    response = requests.get(settings.economic_calendar_url, timeout=15)
    response.raise_for_status()
    raw_events = response.json()

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=LOOKAHEAD_HOURS)

    high_impact_upcoming = []
    for event in raw_events:
        event_time = _parse_event_time(event.get("date", ""))
        if event_time is None or not (now <= event_time <= horizon):
            continue

        impact = str(event.get("impact", "")).lower()
        currency = str(event.get("country", "")).upper()

        if impact == "high" and (not RELEVANT_CURRENCIES or currency in RELEVANT_CURRENCIES):
            high_impact_upcoming.append(
                {
                    "title": event.get("title"),
                    "currency": currency,
                    "time_utc": event_time.isoformat(),
                    "forecast": event.get("forecast"),
                    "previous": event.get("previous"),
                }
            )

    high_impact_upcoming.sort(key=lambda e: e["time_utc"])

    return {
        "fetched_at": now.isoformat(),
        "lookahead_hours": LOOKAHEAD_HOURS,
        "relevant_currencies": sorted(RELEVANT_CURRENCIES),
        "high_impact_upcoming": high_impact_upcoming,
        "raw_event_count": len(raw_events),
    }


def main() -> None:
    result = fetch_calendar()

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = DATA_RAW_DIR / f"economic_calendar_{date_str}.json"
    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    logger.info(
        "%d High-Impact-Events im %dh-Fenster -> %s",
        len(result["high_impact_upcoming"]),
        LOOKAHEAD_HOURS,
        out_path,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Economic-Calendar-Fetch fehlgeschlagen")
        sys.exit(1)
