"""
Browser manager module.
Configures and initializes Selenium Chrome WebDriver with robust options and drivers.
"""
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import HEADLESS, WINDOW_SIZE
from utils.logger import logger


class BrowserManager:
    """Manages creation, configuration, and teardown of Selenium WebDriver instances."""

    def __init__(self, headless: Optional[bool] = None, window_size: Optional[str] = None):
        self.headless = HEADLESS if headless is None else headless
        self.window_size = WINDOW_SIZE if window_size is None else window_size
        self.driver: Optional[webdriver.Chrome] = None

    def _build_chrome_options(self) -> Options:
        """Constructs and returns ChromeOptions with optimized arguments."""
        options = Options()
        options.page_load_strategy = "eager"

        if self.headless:
            # Modern headless mode in Chrome / Selenium 4+
            options.add_argument("--headless=new")

        if self.window_size:
            options.add_argument(f"--window-size={self.window_size}")

        # Performance, stability, and anti-crash arguments
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Standard modern User-Agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        # Suppress logging noise
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def get_driver(self) -> webdriver.Chrome:
        """
        Creates and returns an active Chrome WebDriver.
        Attempts Selenium Manager / webdriver-manager automatically.
        """
        if self.driver is not None:
            return self.driver

        options = self._build_chrome_options()
        driver = None

        # Strategy 1: Direct Selenium 4+ WebDriver (uses built-in Selenium Manager)
        try:
            driver = webdriver.Chrome(options=options)
            logger.info("Chrome WebDriver initialized successfully via Selenium.")
        except Exception as e1:
            logger.warning(f"Standard Chrome initialization failed ({e1}). Trying webdriver-manager...")
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("Chrome WebDriver initialized using webdriver-manager.")
            except Exception as e2:
                logger.error(f"Failed to start Chrome WebDriver: {e2}")
                raise RuntimeError(
                    f"Could not initialize Chrome WebDriver. Ensure Google Chrome is installed. Details: {e2}"
                )

        self.driver = driver
        return self.driver

    def close_driver(self) -> None:
        """Safely closes the browser and frees resources."""
        if self.driver is not None:
            try:
                self.driver.quit()
                logger.info("Chrome WebDriver closed successfully.")
            except Exception as e:
                logger.warning(f"Error during WebDriver shutdown: {e}")
            finally:
                self.driver = None
