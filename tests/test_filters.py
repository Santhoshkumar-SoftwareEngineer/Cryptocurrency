"""
Unit tests for filtering and search service.
"""
# pyrefly: ignore [missing-import]
import pytest
from models.crypto import CryptoCoin
from services.filter_service import (
    filter_by_price,
    filter_by_change,
    get_top_gainers,
    get_top_losers,
    search_coin,
)


@pytest.fixture
def sample_coins():
    """Provides a sample list of CryptoCoin objects for testing."""
    return [
        CryptoCoin(
            rank=1,
            name="Bitcoin",
            symbol="BTC",
            price=67000.0,
            change_24h=2.5,
            market_cap=1300000000000.0,
            volume_24h=30000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
        CryptoCoin(
            rank=2,
            name="Ethereum",
            symbol="ETH",
            price=2500.0,
            change_24h=-1.2,
            market_cap=300000000000.0,
            volume_24h=15000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
        CryptoCoin(
            rank=3,
            name="Tether",
            symbol="USDT",
            price=1.0,
            change_24h=0.01,
            market_cap=110000000000.0,
            volume_24h=40000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
        CryptoCoin(
            rank=4,
            name="Solana",
            symbol="SOL",
            price=150.0,
            change_24h=8.4,
            market_cap=70000000000.0,
            volume_24h=5000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
        CryptoCoin(
            rank=5,
            name="Dogecoin",
            symbol="DOGE",
            price=0.12,
            change_24h=-5.6,
            market_cap=17000000000.0,
            volume_24h=1000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
    ]


class TestFilters:
    """Test suite for filter_service."""

    def test_filter_by_price_min(self, sample_coins):
        filtered = filter_by_price(sample_coins, min_price=1000.0)
        assert len(filtered) == 2
        symbols = [c["symbol"] for c in filtered]
        assert "BTC" in symbols
        assert "ETH" in symbols

    def test_filter_by_price_max(self, sample_coins):
        filtered = filter_by_price(sample_coins, max_price=10.0)
        assert len(filtered) == 2
        symbols = [c["symbol"] for c in filtered]
        assert "USDT" in symbols
        assert "DOGE" in symbols

    def test_filter_by_price_range(self, sample_coins):
        filtered = filter_by_price(sample_coins, min_price=100.0, max_price=3000.0)
        assert len(filtered) == 2
        symbols = [c["symbol"] for c in filtered]
        assert "ETH" in symbols
        assert "SOL" in symbols

    def test_filter_by_change(self, sample_coins):
        gainers = filter_by_change(sample_coins, min_change=1.0)
        assert len(gainers) == 2  # BTC (+2.5%), SOL (+8.4%)

        losers = filter_by_change(sample_coins, max_change=0.0)
        assert len(losers) == 2  # ETH (-1.2%), DOGE (-5.6%)

    def test_get_top_gainers(self, sample_coins):
        top_gainers = get_top_gainers(sample_coins, count=2)
        assert len(top_gainers) == 2
        assert top_gainers[0]["symbol"] == "SOL"
        assert top_gainers[1]["symbol"] == "BTC"

    def test_get_top_losers(self, sample_coins):
        top_losers = get_top_losers(sample_coins, count=2)
        assert len(top_losers) == 2
        assert top_losers[0]["symbol"] == "DOGE"
        assert top_losers[1]["symbol"] == "ETH"

    def test_search_coin(self, sample_coins):
        # Search by exact name
        res = search_coin(sample_coins, "Bitcoin")
        assert len(res) == 1
        assert res[0]["symbol"] == "BTC"

        # Search by lowercase symbol / substring
        res = search_coin(sample_coins, "eth")
        assert len(res) == 2  # ETH and Tether

        # Search by partial symbol
        res = search_coin(sample_coins, "sol")
        assert len(res) == 1
        assert res[0]["name"] == "Solana"

        # Non-matching search
        res = search_coin(sample_coins, "Cardano")
        assert len(res) == 0
