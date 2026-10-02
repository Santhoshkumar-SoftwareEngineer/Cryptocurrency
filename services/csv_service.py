"""
CSV data storage service.
Handles persisting latest market snapshots and logging historical data.
Uses pandas when available, with a resilient pure-Python csv fallback.
"""
import csv
import os
from pathlib import Path
from typing import List, Union, Dict, Any, Optional

try:
    import pandas as pd
    HAS_PANDAS = True
except (ImportError, Exception):
    HAS_PANDAS = False
    pd = None

from models.crypto import CryptoCoin
from config.settings import LATEST_CSV_PATH, HISTORY_CSV_PATH, DATA_DIR
from utils.logger import logger

CSV_COLUMNS = [
    "timestamp",
    "rank",
    "name",
    "symbol",
    "price",
    "change_24h",
    "market_cap",
    "volume_24h",
]


def _coin_to_row(coin: CryptoCoin) -> Dict[str, Any]:
    """Serializes a CryptoCoin instance to a dictionary for CSV output."""
    d = coin.to_dict()
    return {col: d.get(col) for col in CSV_COLUMNS}


def save_latest(coins: List[CryptoCoin], file_path: Union[str, Path] = LATEST_CSV_PATH) -> None:
    """
    Overwrites the latest crypto CSV file with the newest scraping results.
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if HAS_PANDAS and pd is not None:
            try:
                data = [c.to_dict() for c in coins]
                df = pd.DataFrame(data)
                if df.empty:
                    df = pd.DataFrame(columns=CSV_COLUMNS)
                else:
                    df = df[CSV_COLUMNS]
                df.to_csv(path, index=False, encoding="utf-8")
                logger.info(f"Saved latest data ({len(coins)} coins) to {path}")
                return
            except Exception as e:
                logger.warning(f"pandas save_latest failed ({e}), falling back to standard csv module.")

        # Standard library CSV fallback
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            for coin in coins:
                writer.writerow(_coin_to_row(coin))

        logger.info(f"Saved latest data ({len(coins)} coins) to {path}")
    except Exception as e:
        logger.error(f"Error saving latest data to CSV {file_path}: {e}")
        raise


def append_history(coins: List[CryptoCoin], file_path: Union[str, Path] = HISTORY_CSV_PATH) -> None:
    """
    Appends the scraped results to the historical CSV file.
    Creates header only if the file does not exist or is empty.
    """
    if not coins:
        return

    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = path.exists() and path.stat().st_size > 0

        if HAS_PANDAS and pd is not None:
            try:
                data = [c.to_dict() for c in coins]
                df = pd.DataFrame(data)[CSV_COLUMNS]
                df.to_csv(
                    path,
                    mode="a" if file_exists else "w",
                    header=not file_exists,
                    index=False,
                    encoding="utf-8"
                )
                logger.info(f"Historical data appended ({len(coins)} records) to {path}")
                return
            except Exception as e:
                logger.warning(f"pandas append_history failed ({e}), falling back to standard csv module.")

        # Standard library CSV fallback
        with open(path, mode="a" if file_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            if not file_exists:
                writer.writeheader()
            for coin in coins:
                writer.writerow(_coin_to_row(coin))

        logger.info(f"Historical data appended ({len(coins)} records) to {path}")
    except Exception as e:
        logger.error(f"Error appending history data to CSV {file_path}: {e}")
        raise


def load_latest(file_path: Union[str, Path] = LATEST_CSV_PATH) -> List[Dict[str, Any]]:
    """
    Loads latest crypto records from CSV as a list of dictionaries.
    """
    path = Path(file_path)
    if not path.exists() or path.stat().st_size == 0:
        logger.warning(f"Latest CSV not found or empty: {file_path}")
        return []

    records = []
    try:
        with open(path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                record = dict(row)
                for num_field in ("rank",):
                    if record.get(num_field):
                        try:
                            record[num_field] = int(record[num_field])
                        except ValueError:
                            pass
                for float_field in ("price", "change_24h", "market_cap", "volume_24h"):
                    if record.get(float_field) and record[float_field] != "":
                        try:
                            record[float_field] = float(record[float_field])
                        except ValueError:
                            record[float_field] = None
                    else:
                        record[float_field] = None
                records.append(record)
        return records
    except Exception as e:
        logger.error(f"Error reading latest CSV {file_path}: {e}")
        return []


def load_history(file_path: Union[str, Path] = HISTORY_CSV_PATH) -> List[Dict[str, Any]]:
    """
    Loads historical crypto records from CSV as a list of dictionaries.
    """
    return load_latest(file_path)
