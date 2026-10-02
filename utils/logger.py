"""
Logger utility module for Cryptocurrency Price Tracker.
Provides unified logging to console and file (logs/app.log).
"""
import logging
import sys
from config.settings import LOG_FILE_PATH, LOG_LEVEL, LOGS_DIR

def setup_logger(name: str = "crypto_tracker") -> logging.Logger:
    """Configures and returns a logger instance."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Avoid duplicate handlers if already added
    if not logger.handlers:
        # File handler formatted as 'YYYY-MM-DD HH:MM:SS LEVEL Message'
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
        file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler (optional stream for warnings/errors or clean terminal display)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)  # Reserve console stream for errors only
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
