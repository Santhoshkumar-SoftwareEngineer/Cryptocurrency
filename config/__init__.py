"""Configuration package for Cryptocurrency Price Tracker."""
from .settings import (
    HEADLESS,
    WINDOW_SIZE,
    SCRAPE_LIMIT,
    SCRAPE_INTERVAL,
    PAGE_TIMEOUT,
    COINMARKETCAP_URL,
    LOG_LEVEL,
    DATA_DIR,
    LOGS_DIR,
    LATEST_CSV_PATH,
    HISTORY_CSV_PATH,
    LOG_FILE_PATH,
)

__all__ = [
    "HEADLESS",
    "WINDOW_SIZE",
    "SCRAPE_LIMIT",
    "SCRAPE_INTERVAL",
    "PAGE_TIMEOUT",
    "COINMARKETCAP_URL",
    "LOG_LEVEL",
    "DATA_DIR",
    "LOGS_DIR",
    "LATEST_CSV_PATH",
    "HISTORY_CSV_PATH",
    "LOG_FILE_PATH",
]
