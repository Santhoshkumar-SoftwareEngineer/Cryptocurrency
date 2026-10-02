"""
Unit tests for statistics calculation service.
"""
import pytest
from models.crypto import CryptoCoin
from services.statistics import calculate_statistics


@pytest.fixture
def sample_coins():
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
            change_24h=-1.5,
            market_cap=300000000000.0,
            volume_24h=15000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
        CryptoCoin(
            rank=3,
            name="Solana",
            symbol="SOL",
            price=150.0,
            change_24h=10.0,
            market_cap=70000000000.0,
            volume_24h=5000000000.0,
            timestamp="2026-10-01 19:30:00"
        ),
    ]


class TestStatistics:
    """Test suite for statistics calculation."""

    def test_calculate_statistics_populated(self, sample_coins):
        stats = calculate_statistics(sample_coins)

        assert stats["total_coins"] == 3
        assert stats["highest_gainer"]["symbol"] == "SOL"
        assert stats["highest_gainer"]["change_24h"] == 10.0
        assert stats["highest_loser"]["symbol"] == "ETH"
        assert stats["highest_loser"]["change_24h"] == -1.5
        assert stats["highest_market_cap"]["symbol"] == "BTC"
        assert stats["highest_market_cap"]["market_cap"] == 1300000000000.0
        # Average change: (2.5 - 1.5 + 10.0) / 3 = 11.0 / 3 = 3.67
        assert stats["average_change_24h"] == 3.67
        assert stats["timestamp"] == "2026-10-01 19:30:00"

    def test_calculate_statistics_empty(self):
        stats = calculate_statistics([])
        assert stats["total_coins"] == 0
        assert stats["highest_gainer"] is None
        assert stats["highest_loser"] is None
        assert stats["highest_market_cap"] is None
        assert stats["average_change_24h"] is None
        assert stats["timestamp"] is None
