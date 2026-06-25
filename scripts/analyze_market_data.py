"""Berechnet FVGs und Equal Highs/Lows aus den rohen Marktdaten.

Erzeugt `data/raw/analysis_<YYYY-MM-DD>.json` mit vorberechneten Strukturen,
damit der Report-Schritt diese nicht mehr inline ableiten muss.

FVG-Definition (korrekt):
  Bullish FVG: Kerze i ist eine Aufwärtskerze und das Low von Kerze i+1
               liegt ÜBER dem High von Kerze i-1 → ungeschlossene Gap nach oben.
  Bearish FVG: Kerze i ist eine Abwärtskerze und das High von Kerze i+1
               liegt UNTER dem Low von Kerze i-1 → ungeschlossene Gap nach unten.

Equal Highs/Lows:
  Equal Highs: Swing-Highs die innerhalb der Toleranz beieinander liegen UND
               über dem aktuellen Preis → sell-side Liquidität.
  Equal Lows:  Swing-Lows innerhalb der Toleranz UND unter dem aktuellen Preis
               → buy-side Liquidität.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from config import DATA_RAW_DIR, load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("analyze_market_data")

EQH_EQL_TOLERANCE = 0.0005  # 0.05 %


def find_fvgs(candles: list[dict], max_results: int = 5) -> list[dict]:
    """Findet die größten ungeschlossenen FVGs in den letzten `candles`.

    Iteriert über Triplets (i-1, i, i+1). Ein FVG gilt als 'offen' wenn der
    Preis die Gap-Zone noch nicht vollständig durchquert hat.
    """
    if len(candles) < 3:
        return []

    fvgs: list[dict] = []
    current_price = candles[-1]["close"]

    for i in range(1, len(candles) - 1):
        prev = candles[i - 1]
        curr = candles[i]
        nxt  = candles[i + 1]

        # Bullish FVG: Gap nach oben — Low der rechten Kerze > High der linken Kerze
        if nxt["low"] > prev["high"]:
            top    = nxt["low"]
            bottom = prev["high"]
            size   = top - bottom
            # Offen wenn aktueller Preis noch in oder unter der Gap liegt
            is_open = current_price <= top
            fvgs.append({
                "type":       "bullish",
                "time_utc":   curr["time_utc"],
                "top":        round(top, 4),
                "bottom":     round(bottom, 4),
                "size":       round(size, 4),
                "open":       is_open,
            })

        # Bearish FVG: Gap nach unten — High der rechten Kerze < Low der linken Kerze
        elif nxt["high"] < prev["low"]:
            top    = prev["low"]
            bottom = nxt["high"]
            size   = top - bottom
            # Offen wenn aktueller Preis noch in oder über der Gap liegt
            is_open = current_price >= bottom
            fvgs.append({
                "type":       "bearish",
                "time_utc":   curr["time_utc"],
                "top":        round(top, 4),
                "bottom":     round(bottom, 4),
                "size":       round(size, 4),
                "open":       is_open,
            })

    # Nur offene, sortiert nach Größe
    open_fvgs = [f for f in fvgs if f["open"]]
    open_fvgs.sort(key=lambda x: x["size"], reverse=True)
    return open_fvgs[:max_results]


def find_equal_highs_lows(
    candles: list[dict],
    tolerance: float = EQH_EQL_TOLERANCE,
    lookback: int = 120,
) -> dict:
    """Findet Equal Highs und Equal Lows als Liquiditätszonen.

    Equal Highs sind ÜBER dem aktuellen Preis (sell-side liquidity).
    Equal Lows sind UNTER dem aktuellen Preis (buy-side liquidity).
    Gibt Gruppen von mindestens 2 Kerzen zurück, deren High/Low innerhalb
    der Toleranz liegt.
    """
    candles = candles[-lookback:]
    if not candles:
        return {"equal_highs": [], "equal_lows": []}

    current_price = candles[-1]["close"]

    highs = [(c["time_utc"], c["high"]) for c in candles]
    lows  = [(c["time_utc"], c["low"])  for c in candles]

    def cluster(points: list[tuple[str, float]], above_price: bool) -> list[dict]:
        result: list[dict] = []
        used = [False] * len(points)
        for i, (t_i, v_i) in enumerate(points):
            if used[i]:
                continue
            # Preis-Seite filtern — Equal Highs müssen über, Equal Lows unter aktuellem Preis liegen
            if above_price and v_i <= current_price:
                continue
            if not above_price and v_i >= current_price:
                continue
            group = [(t_i, v_i)]
            for j in range(i + 1, len(points)):
                if used[j]:
                    continue
                _, v_j = points[j]
                if abs(v_j - v_i) / v_i <= tolerance:
                    group.append(points[j])
                    used[j] = True
            if len(group) >= 2:
                avg_level = sum(v for _, v in group) / len(group)
                result.append({
                    "level":   round(avg_level, 4),
                    "count":   len(group),
                    "touches": [t for t, _ in group],
                })
        result.sort(key=lambda x: x["level"])
        return result

    return {
        "equal_highs": cluster(highs, above_price=True),
        "equal_lows":  cluster(lows,  above_price=False),
    }


def analyze_symbol(symbol_data: dict) -> dict:
    candles_5m = symbol_data.get("intraday_5m", [])
    lookback   = candles_5m[-120:] if len(candles_5m) >= 120 else candles_5m

    fvgs   = find_fvgs(lookback)
    eqhl   = find_equal_highs_lows(candles_5m)

    return {
        "symbol":       symbol_data["symbol"],
        "fvgs_top5":    fvgs,
        "equal_highs":  eqhl["equal_highs"],
        "equal_lows":   eqhl["equal_lows"],
        "current_price": round(candles_5m[-1]["close"], 4) if candles_5m else None,
    }


def main() -> None:
    date_str  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data_file = DATA_RAW_DIR / f"market_data_{date_str}.json"

    if not data_file.exists():
        logger.error("market_data_%s.json nicht gefunden – fetch_market_data.py zuerst ausführen", date_str)
        sys.exit(1)

    raw = json.loads(data_file.read_text(encoding="utf-8"))

    result = {
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
        "gold":        analyze_symbol(raw["gold"]),
        "us500":       analyze_symbol(raw["us500"]),
    }

    out_path = DATA_RAW_DIR / f"analysis_{date_str}.json"
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info(
        "Gold: %d FVGs, %d EQH, %d EQL | US500: %d FVGs, %d EQH, %d EQL -> %s",
        len(result["gold"]["fvgs_top5"]),
        len(result["gold"]["equal_highs"]),
        len(result["gold"]["equal_lows"]),
        len(result["us500"]["fvgs_top5"]),
        len(result["us500"]["equal_highs"]),
        len(result["us500"]["equal_lows"]),
        out_path,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Analyse fehlgeschlagen")
        sys.exit(1)
