"""
Market summary statistics calculation service.
Computes key performance indicators across cryptocurrency snapshots.
"""
from typing import Dict, Any, List, Optional
from models.crypto import CryptoCoin
from services.filter_service import _to_list_of_dicts


def calculate_statistics(data: Any) -> Dict[str, Any]:
    """
    Computes key summary statistics across the provided cryptocurrency data snapshot.
    Returns:
        total_coins (int)
        highest_gainer (dict | None)
        highest_loser (dict | None)
        highest_market_cap (dict | None)
        average_change_24h (float | None)
        timestamp (str | None)
    """
    records = _to_list_of_dicts(data)

    if not records:
        return {
            "total_coins": 0,
            "highest_gainer": None,
            "highest_loser": None,
            "highest_market_cap": None,
            "average_change_24h": None,
            "timestamp": None,
        }

    total_coins = len(records)
    timestamp: Optional[str] = records[0].get("timestamp") if records else None

    # Filter records with valid change_24h
    valid_changes = []
    for r in records:
        c = r.get("change_24h")
        if c is not None:
            try:
                valid_changes.append((float(c), r))
            except (ValueError, TypeError):
                pass

    highest_gainer = None
    highest_loser = None
    avg_change = None

    if valid_changes:
        valid_changes.sort(key=lambda x: x[0])
        loser_val, loser_row = valid_changes[0]
        gainer_val, gainer_row = valid_changes[-1]

        highest_loser = {
            "name": str(loser_row.get("name")),
            "symbol": str(loser_row.get("symbol")),
            "change_24h": loser_val,
            "price": loser_row.get("price"),
        }
        highest_gainer = {
            "name": str(gainer_row.get("name")),
            "symbol": str(gainer_row.get("symbol")),
            "change_24h": gainer_val,
            "price": gainer_row.get("price"),
        }
        avg_change = round(sum(val for val, _ in valid_changes) / len(valid_changes), 2)

    # Filter records with valid market_cap
    valid_mcaps = []
    for r in records:
        m = r.get("market_cap")
        if m is not None:
            try:
                valid_mcaps.append((float(m), r))
            except (ValueError, TypeError):
                pass

    highest_market_cap = None
    if valid_mcaps:
        valid_mcaps.sort(key=lambda x: x[0], reverse=True)
        mcap_val, mcap_row = valid_mcaps[0]
        highest_market_cap = {
            "name": str(mcap_row.get("name")),
            "symbol": str(mcap_row.get("symbol")),
            "market_cap": mcap_val,
            "price": mcap_row.get("price"),
        }

    return {
        "total_coins": total_coins,
        "highest_gainer": highest_gainer,
        "highest_loser": highest_loser,
        "highest_market_cap": highest_market_cap,
        "average_change_24h": avg_change,
        "timestamp": timestamp,
    }
