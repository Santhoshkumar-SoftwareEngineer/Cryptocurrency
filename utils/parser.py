"""
Data parsing and cleaning utilities.
Converts raw scraped strings into typed Python numeric and string representations.
"""
import re
from typing import Optional


def parse_rank(raw_text: Optional[str]) -> Optional[int]:
    """
    Parses rank string into an integer.
    Examples: '1', '#1', ' 10 ' -> 1, 1, 10
    """
    if raw_text is None:
        return None
    cleaned = re.sub(r"[^\d]", "", str(raw_text).strip())
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def parse_currency(raw_text: Optional[str]) -> Optional[float]:
    """
    Parses currency string into a float, supporting abbreviations (K, M, B, T)
    and non-standard Unicode whitespaces (\u202f, \xa0).
    Examples:
        '$67,000.50'     -> 67000.50
        '$\u202f1.3T'    -> 1300000000000.0
        '$25.4B'         -> 25400000000.0
        '$850M'          -> 850000000.0
        '$10.5K'         -> 10500.0
        '$0.00012'       -> 0.00012
    """
    if raw_text is None:
        return None

    text = str(raw_text).strip()
    if not text or text in ("--", "N/A", "NaN", "null"):
        return None

    # Check for negative value
    is_negative = "-" in text or "(" in text

    # Remove currency symbols, commas, spaces (including narrow NBSP \u202f and \xa0), parentheses
    cleaned = re.sub(r"[\$,\s\(\)\u202f\xa0\u200b]", "", text)

    # Match numeric part with optional multiplier suffix (K, M, B, T)
    match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*([KkMmBbTt])?", cleaned)
    if not match:
        return None

    number_str, suffix = match.groups()
    try:
        val = float(number_str)
    except ValueError:
        return None

    multiplier = 1.0
    if suffix:
        s = suffix.upper()
        if s == "K":
            multiplier = 1e3
        elif s == "M":
            multiplier = 1e6
        elif s == "B":
            multiplier = 1e9
        elif s == "T":
            multiplier = 1e12

    result = val * multiplier
    if is_negative and result > 0:
        result = -result
    return result


def parse_percentage(raw_text: Optional[str]) -> Optional[float]:
    """
    Parses percentage string into a float.
    Handles + / - signs, percentages, and direction indicators (▲, ▼, etc.).
    Examples:
        '2.35%'   -> 2.35
        '+2.35%'  -> 2.35
        '-1.50%'  -> -1.50
        '▲ 2.50%' -> 2.50
        '▼ 1.20%' -> -1.20
    """
    if raw_text is None:
        return None

    text = str(raw_text).strip()
    if not text or text in ("--", "N/A", "NaN", "null"):
        return None

    # Check for down indicator
    is_negative = "-" in text or "▼" in text or "down" in text.lower() or "caret-down" in text.lower()

    # Extract digits with optional decimal point
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None

    try:
        val = float(match.group(1))
        return -val if is_negative else val
    except ValueError:
        return None


def parse_market_cap(raw_text: Optional[str]) -> Optional[float]:
    """
    Parses market capitalization string.
    Examples:
        '$1.3T' -> 1300000000000.0
        '$850M' -> 850000000.0
        '$25.4B' -> 25400000000.0
        '$1,300,000,000,000' -> 1300000000000.0
    """
    return parse_currency(raw_text)


def parse_volume(raw_text: Optional[str]) -> Optional[float]:
    """
    Parses 24-hour trading volume string.
    Examples:
        '$30,000,000,000' -> 30000000000.0
        '$30B' -> 30000000000.0
        '$850M' -> 850000000.0
    """
    if raw_text is None:
        return None
    first_part = str(raw_text).split("\n")[0].split("/")[0].strip()
    return parse_currency(first_part)
