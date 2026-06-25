"""Holt OHLC-Daten für Gold (Proxy für XAUUSD) und US500 über Yahoo Finance (yfinance).
Kostenlos, kein API-Key, kein Login. Liefert die Rohdaten, auf denen die Routine dann
Session-Highs/Lows, FVGs, Equal-Highs/Lows etc. gegen das Rulebook prüft.

Wichtige Einschränkung: Yahoo-Daten sind keine 1:1-Kopie deines FundedElite-Feeds
(Symbol-Mapping/Spread unterscheidet sich leicht). Für Session-Level-Analyse auf
5m/1h-Basis ist die Abweichung in der Praxis gering, für exakte Tick-Execution-Daten
reicht das nicht.

Zwei Zeitebenen pro Symbol:
- 5m, letzte 5 Tage: Session-Highs/Lows, FVGs auf Entry-Timeframe.
- 1h, letzter Monat: HTF-Bias/Kontext.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

import yfinance as yf

from config import DATA_RAW_DIR, load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_market_data")


def _candles_to_records(df) -> list[dict]:
    if df.empty:
        return []
    df = df.tz_convert("UTC") if df.index.tz is not None else df.tz_localize("UTC")
    records = []
    for ts, row in df.iterrows():
        records.append(
            {
                "time_utc": ts.isoformat(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": float(row["Volume"]) if "Volume" in row else None,
            }
        )
    return records


def fetch_symbol(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)

    intraday = ticker.history(period="5d", interval="5m")
    htf = ticker.history(period="1mo", interval="1h")

    return {
        "symbol": symbol,
        "intraday_5m": _candles_to_records(intraday),
        "htf_1h": _candles_to_records(htf),
    }


def main() -> None:
    settings = load_settings()
    now = datetime.now(timezone.utc)

    result = {
        "fetched_at": now.isoformat(),
        "gold": fetch_symbol(settings.gold_symbol),
        "us500": fetch_symbol(settings.us500_symbol),
    }

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    date_str = now.strftime("%Y-%m-%d")
    out_path = DATA_RAW_DIR / f"market_data_{date_str}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    logger.info(
        "Gold: %d/%d Candles, US500: %d/%d Candles -> %s",
        len(result["gold"]["intraday_5m"]),
        len(result["gold"]["htf_1h"]),
        len(result["us500"]["intraday_5m"]),
        len(result["us500"]["htf_1h"]),
        out_path,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Market-Data-Fetch fehlgeschlagen")
        sys.exit(1)
