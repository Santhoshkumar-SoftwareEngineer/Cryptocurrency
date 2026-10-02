"""
Logger utility module for Cryptocurrency Price Tracker.
Provides unified logging to console and file (logs/app.log).
"""
import logging
import sys
from config.settings import LOG_FILE_PATH, LOG_LEVEL, LOGS_DIR

def setup_logger(name: str = "crypto_tracker") -> logging.Logger:
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # Avoid duplicate handlers if already added
    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Attempt to create file handler, fallback gracefully if filesystem is read-only
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
            file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError):
            pass

        # Console handler (standard output stream for cloud/serverless/terminals)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger()
