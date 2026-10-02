"""
Validation utilities for cryptocurrency data.
"""
from typing import Any, Dict


def validate_coin_data(coin_dict: Dict[str, Any]) -> bool:
    """
    Validates that essential coin fields are present and well-formed.
    """
    if not isinstance(coin_dict, dict):
        return False

    name = coin_dict.get("name")
    symbol = coin_dict.get("symbol")

    if not name or not isinstance(name, str) or not name.strip():
        return False
    if not symbol or not isinstance(symbol, str) or not symbol.strip():
        return False

    # Rank should be positive int if present
    rank = coin_dict.get("rank")
    if rank is not None:
        if not isinstance(rank, int) or rank <= 0:
            return False

    # Price should be non-negative if present
    price = coin_dict.get("price")
    if price is not None:
        if not isinstance(price, (int, float)) or price < 0:
            return False

    return True
