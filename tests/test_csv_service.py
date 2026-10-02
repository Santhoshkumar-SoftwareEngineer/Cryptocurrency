"""
Unit tests for CSV storage service.
"""
import pytest
from pathlib import Path
from models.crypto import CryptoCoin
from services.csv_service import (
    save_latest,
    append_history,
    load_latest,
    load_history,
)


@pytest.fixture
def temp_csv_paths(tmp_path):
    latest_path = tmp_path / "crypto_latest.csv"
    history_path = tmp_path / "crypto_history.csv"
    return latest_path, history_path


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
    ]


class TestCsvService:
    """Test suite for csv_service."""

    def test_save_and_load_latest(self, temp_csv_paths, sample_coins):
        latest_path, _ = temp_csv_paths

        save_latest(sample_coins, file_path=latest_path)
        assert latest_path.exists()

        records = load_latest(file_path=latest_path)
        assert len(records) == 2
        assert [c["symbol"] for c in records] == ["BTC", "ETH"]
        assert records[0]["price"] == 67000.0

    def test_append_and_load_history(self, temp_csv_paths, sample_coins):
        _, history_path = temp_csv_paths

        # First append (creates file with header)
        append_history(sample_coins, file_path=history_path)
        assert history_path.exists()

        records1 = load_history(file_path=history_path)
        assert len(records1) == 2

        # Second append (appends rows without duplicating header)
        append_history(sample_coins, file_path=history_path)
        records2 = load_history(file_path=history_path)
        assert len(records2) == 4
