"""Holt den aktuellen Account-Snapshot (Equity, Balance, Margin, offene Positionen)
über die MetaApi RPC-Connection. Read-only (Investor-Passwort am Account in MetaApi
ist ausreichend und vorzuziehen, falls FundedElite eines anbietet).

Quelle MetaApi Python SDK Pattern: api.metatrader_account_api.get_account() ->
account.get_rpc_connection() -> connection.get_account_information() / get_positions().
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone

from metaapi_cloud_sdk import MetaApi

from config import DATA_RAW_DIR, load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_account_snapshot")


async def fetch_snapshot() -> dict:
    settings = load_settings()

    api = MetaApi(settings.metaapi_token)
    account = await api.metatrader_account_api.get_account(settings.metaapi_account_id)

    if account.state != "DEPLOYED":
        logger.info("Account state=%s, starte Deploy...", account.state)
        await account.deploy()

    await account.wait_connected()

    connection = account.get_rpc_connection()
    await connection.connect()
    await connection.wait_synchronized()

    try:
        account_information = await connection.get_account_information()
        positions = await connection.get_positions()
    finally:
        await connection.close()

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "account_information": account_information,
        "open_positions": positions,
    }


def main() -> None:
    snapshot = asyncio.run(fetch_snapshot())

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = DATA_RAW_DIR / f"account_snapshot_{date_str}.json"
    out_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    logger.info("Snapshot geschrieben: %s", out_path)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Account-Snapshot-Fetch fehlgeschlagen")
        sys.exit(1)
