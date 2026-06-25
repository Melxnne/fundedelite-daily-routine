"""Zentrale Konfiguration für alle Fetch-Scripts.

Lädt Settings aus Umgebungsvariablen (lokal über .env via python-dotenv, in der
Cloud Routine über die dort konfigurierten Env-Vars). Keine Secrets mehr nötig -
weder Yahoo Finance noch der ForexFactory-Feed brauchen Auth.
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


def _optional(name: str, default: str) -> str:
    return os.getenv(name, default)


@dataclass(frozen=True)
class Settings:
    gold_symbol: str
    us500_symbol: str
    economic_calendar_url: str


def load_settings() -> Settings:
    return Settings(
        # GC=F = COMEX-Gold-Future, handelt nahezu durchgehend -> bildet
        # Session-Verhalten (Asia/London/NY) besser ab als ein reiner Spot-Feed.
        gold_symbol=_optional("MARKET_SYMBOL_GOLD", "GC=F"),
        # ES=F = E-mini S&P 500 Future, ebenfalls nahezu 24h gehandelt.
        us500_symbol=_optional("MARKET_SYMBOL_US500", "ES=F"),
        economic_calendar_url=_optional(
            "ECONOMIC_CALENDAR_URL",
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
        ),
    )
