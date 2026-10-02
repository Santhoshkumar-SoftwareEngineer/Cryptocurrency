"""
Application Configuration and Settings.
Loads configuration from environment variables (.env) with robust fallbacks.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base workspace directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Helper function to parse boolean env vars
def _get_bool(env_var_name: str, default: bool = True) -> bool:
    val = os.getenv(env_var_name)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "yes", "y", "t")

# Helper function to parse integer env vars
def _get_int(env_var_name: str, default: int) -> int:
    val = os.getenv(env_var_name)
    if val is None:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default

# Browser Configuration
HEADLESS: bool = _get_bool("HEADLESS", default=True)
WINDOW_SIZE: str = os.getenv("WINDOW_SIZE", "1920,1080")

# Scraper Configuration
SCRAPE_LIMIT: int = _get_int("SCRAPE_LIMIT", default=10)
SCRAPE_INTERVAL: int = _get_int("SCRAPE_INTERVAL", default=300)
PAGE_TIMEOUT: int = _get_int("PAGE_TIMEOUT", default=25)
COINMARKETCAP_URL: str = os.getenv("COINMARKETCAP_URL", "https://coinmarketcap.com/")

# Logging Configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# Paths and Directories
DATA_DIR: Path = BASE_DIR / "data"
LOGS_DIR: Path = BASE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LATEST_CSV_PATH: Path = DATA_DIR / "crypto_latest.csv"
HISTORY_CSV_PATH: Path = DATA_DIR / "crypto_history.csv"
LOG_FILE_PATH: Path = LOGS_DIR / "app.log"
