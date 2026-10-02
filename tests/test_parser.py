"""
Unit tests for data cleaning and string parsers.
"""
import pytest
from utils.parser import (
    parse_rank,
    parse_currency,
    parse_percentage,
    parse_market_cap,
    parse_volume,
)


class TestParser:
    """Test suite for utils/parser.py"""

    def test_parse_rank(self):
        assert parse_rank("1") == 1
        assert parse_rank("#5") == 5
        assert parse_rank("  10  ") == 10
        assert parse_rank("Rank 100") == 100
        assert parse_rank(None) is None
        assert parse_rank("") is None
        assert parse_rank("N/A") is None

    def test_parse_currency_standard(self):
        assert parse_currency("$67,000.50") == 67000.50
        assert parse_currency("67000.50") == 67000.50
        assert parse_currency("$2,500.00") == 2500.00
        assert parse_currency("$1.00") == 1.00
        assert parse_currency("$0.000125") == 0.000125

    def test_parse_currency_multipliers(self):
        # Trillion
        assert parse_currency("$1.3T") == 1300000000000.0
        assert parse_currency("$1.30T") == 1300000000000.0
        # Billion
        assert parse_currency("$25.4B") == 25400000000.0
        assert parse_currency("$100B") == 100000000000.0
        # Million
        assert parse_currency("$850M") == 850000000.0
        assert parse_currency("$12.5M") == 12500000.0
        # Thousand
        assert parse_currency("$10.5K") == 10500.0

    def test_parse_currency_edge_cases(self):
        assert parse_currency(None) is None
        assert parse_currency("") is None
        assert parse_currency("--") is None
        assert parse_currency("N/A") is None
        assert parse_currency("NaN") is None
        assert parse_currency("null") is None

    def test_parse_percentage(self):
        assert parse_percentage("2.35%") == 2.35
        assert parse_percentage("+2.35%") == 2.35
        assert parse_percentage("-1.50%") == -1.50
        assert parse_percentage("▲ 2.50%") == 2.50
        assert parse_percentage("▼ 1.20%") == -1.20
        assert parse_percentage("0.00%") == 0.0
        assert parse_percentage(None) is None
        assert parse_percentage("") is None
        assert parse_percentage("--") is None

    def test_parse_market_cap(self):
        assert parse_market_cap("$1.3T") == 1300000000000.0
        assert parse_market_cap("$850M") == 850000000.0
        assert parse_market_cap("$25.4B") == 25400000000.0
        assert parse_market_cap("$1,300,000,000,000") == 1300000000000.0

    def test_parse_volume(self):
        assert parse_volume("$30,000,000,000") == 30000000000.0
        assert parse_volume("$30B") == 30000000000.0
        assert parse_volume("$850M / 12,000 BTC") == 850000000.0
        assert parse_volume("$25.4B\n450k ETH") == 25400000000.0
        assert parse_volume(None) is None
