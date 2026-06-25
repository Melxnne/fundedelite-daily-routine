"""Holt geschlossene Trades des Lookback-Fensters (Default 24h) über die MetaStats API.

MetaStats ist Teil von MetaApi und für reine Trade-Monitoring-Zwecke (myfxbook-Style)
gedacht, kein Trading-Zugriff. SDK-Pattern: MetaStats(token).get_account_trades(
    account_id, start_time, end_time
).
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta, timezone

from metaapi_cloud_sdk import MetaStats

from config import DATA_RAW_DIR, load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_trade_history")


async def fetch_trades() -> dict:
    settings = load_settings()
    metastats = MetaStats(settings.metaapi_token)

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=settings.trade_history_lookback_hours)

    trades = await metastats.get_account_trades(
        account_id=settings.metaapi_account_id,
        start_time=start_time.strftime("%Y-%m-%d %H:%M:%S.000"),
        end_time=end_time.strftime("%Y-%m-%d %H:%M:%S.000"),
    )

    return {
        "fetched_at": end_time.isoformat(),
        "lookback_hours": settings.trade_history_lookback_hours,
        "trades": trades,
    }


def main() -> None:
    result = asyncio.run(fetch_trades())

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = DATA_RAW_DIR / f"trade_history_{date_str}.json"
    out_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    logger.info("%d Trades geschrieben nach %s", len(result["trades"]), out_path)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Trade-History-Fetch fehlgeschlagen")
        sys.exit(1)
