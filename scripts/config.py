"""Zentrale Konfiguration für alle Fetch-Scripts.

Lädt Secrets/Settings aus Umgebungsvariablen (lokal über .env via python-dotenv,
in der Cloud Routine über die dort konfigurierten Secrets). Keine Defaults für
sicherheitsrelevante Werte (Token, Account-ID) -> fail fast statt silent fallback.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = REPO_ROOT / "data" / "raw"
REPORTS_DIR = REPO_ROOT / "reports"


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Pflicht-Env-Var '{name}' fehlt. Siehe .env.example."
        )
    return value


def _optional(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    metaapi_token: str
    metaapi_account_id: str
    trade_history_lookback_hours: int
    economic_calendar_url: str


def load_settings() -> Settings:
    return Settings(
        metaapi_token=_require("METAAPI_TOKEN"),
        metaapi_account_id=_require("METAAPI_ACCOUNT_ID"),
        trade_history_lookback_hours=int(
            _optional("TRADE_HISTORY_LOOKBACK_HOURS", "24")
        ),
        economic_calendar_url=_optional(
            "ECONOMIC_CALENDAR_URL",
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
        ),
    )
