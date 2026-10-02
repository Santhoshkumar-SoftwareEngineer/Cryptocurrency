"""
Filtering and search service for cryptocurrency data.
Supports operations on lists of CryptoCoin instances, list of dicts, or DataFrames.
"""
from typing import List, Optional, Union, Dict, Any
from models.crypto import CryptoCoin


def _to_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    """Normalizes input data into a list of standard dictionaries."""
    if data is None:
        return []
    if hasattr(data, "to_dict") and callable(getattr(data, "to_dict")):
        # If it's a DataFrame
        try:
            return data.to_dict(orient="records")
        except Exception:
            pass
    if isinstance(data, list):
        out = []
        for item in data:
            if isinstance(item, CryptoCoin):
                out.append(item.to_dict())
            elif isinstance(item, dict):
                out.append(dict(item))
        return out
    return []


def filter_by_price(
    data: Any,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Filters cryptocurrency records by minimum and/or maximum price.
    """
    records = _to_list_of_dicts(data)
    results = []

    for coin in records:
        price = coin.get("price")
        if price is None:
            continue
        try:
            p = float(price)
        except (ValueError, TypeError):
            continue

        if min_price is not None and p < min_price:
            continue
        if max_price is not None and p > max_price:
            continue
        results.append(coin)

    return results


def filter_by_change(
    data: Any,
    min_change: Optional[float] = None,
    max_change: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Filters cryptocurrency records by 24h percentage change range.
    """
    records = _to_list_of_dicts(data)
    results = []

    for coin in records:
        change = coin.get("change_24h")
        if change is None:
            continue
        try:
            c = float(change)
        except (ValueError, TypeError):
            continue

        if min_change is not None and c < min_change:
            continue
        if max_change is not None and c > max_change:
            continue
        results.append(coin)

    return results


def get_top_gainers(
    data: Any,
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    Returns the top N coins with the highest positive 24-hour percentage change.
    """
    records = _to_list_of_dicts(data)
    valid = []
    for c in records:
        ch = c.get("change_24h")
        if ch is not None:
            try:
                c_copy = dict(c)
                c_copy["change_24h"] = float(ch)
                valid.append(c_copy)
            except (ValueError, TypeError):
                pass

    valid.sort(key=lambda x: x["change_24h"], reverse=True)
    return valid[:count]


def get_top_losers(
    data: Any,
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    Returns the top N coins with the largest negative 24-hour percentage change.
    """
    records = _to_list_of_dicts(data)
    valid = []
    for c in records:
        ch = c.get("change_24h")
        if ch is not None:
            try:
                c_copy = dict(c)
                c_copy["change_24h"] = float(ch)
                valid.append(c_copy)
            except (ValueError, TypeError):
                pass

    valid.sort(key=lambda x: x["change_24h"], reverse=False)
    return valid[:count]


def search_coin(
    data: Any,
    query: str
) -> List[Dict[str, Any]]:
    """
    Searches for cryptocurrencies by coin name or symbol (case-insensitive substring).
    """
    records = _to_list_of_dicts(data)
    if not query.strip():
        return records

    q = query.strip().lower()
    results = []
    for coin in records:
        name = str(coin.get("name", "")).lower()
        symbol = str(coin.get("symbol", "")).lower()
        if q in name or q in symbol:
            results.append(coin)

    return results
