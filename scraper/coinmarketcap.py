"""
CoinMarketCap cryptocurrency live market data scraper.
Uses Selenium WebDriver with explicit waits, robust CSS/XPath selectors,
and dynamic page rendering support.
"""
from datetime import datetime
import time
from typing import List, Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

from config.settings import COINMARKETCAP_URL, PAGE_TIMEOUT, SCRAPE_LIMIT
from models.crypto import CryptoCoin
from scraper.browser import BrowserManager
from utils.logger import logger
from utils.parser import parse_rank, parse_currency, parse_percentage, parse_volume
from utils.validators import validate_coin_data


class CoinMarketCapScraper:
    """
    Scraper for extracting top cryptocurrency market data dynamically using Selenium.
    """

    # Centralized CSS and XPath selectors for resilience
    SELECTORS = {
        "cmc_table_rows": "table.cmc-table tbody tr, table tbody tr",
        "cookie_accept": "button#onetrust-accept-btn-handler, button.cmc-cookie-policy-btn, button[id*='accept'], button[name='agree']",
    }

    # Backup live crypto market URLs in case ISP/Firewall blocks CoinMarketCap domain
    BACKUP_MARKET_URLS = [
        "https://coincodex.com/",
        "https://finance.yahoo.com/markets/crypto/all/",
    ]

    def __init__(self, headless: Optional[bool] = None, timeout: int = PAGE_TIMEOUT):
        self.browser_manager = BrowserManager(headless=headless)
        self.driver: Optional[webdriver.Chrome] = None
        self.timeout = timeout
        self.active_source = "coinmarketcap"

    def start_browser(self) -> None:
        """Initializes and opens the Chrome browser instance."""
        if self.driver is None:
            logger.info("Starting Chrome browser instance...")
            self.driver = self.browser_manager.get_driver()
            try:
                self.driver.set_page_load_timeout(15)
                self.driver.set_script_timeout(15)
            except Exception:
                pass

    def open_market_page(self, url: Optional[str] = None) -> None:
        """
        Navigates to CoinMarketCap (or specified URL) and handles initial overlays.
        """
        self.start_browser()
        target_url = url or COINMARKETCAP_URL

        logger.info(f"Navigating to {target_url}...")
        try:
            self.driver.get(target_url)
            self.active_source = "coinmarketcap" if "coinmarketcap" in target_url else "other"
            self._handle_cookie_consent()
        except (WebDriverException, TimeoutException) as e:
            logger.warning(f"Connection/timeout accessing {target_url}: {e}")
            if target_url == COINMARKETCAP_URL:
                # Attempt backup live sources sequentially
                for backup_url in self.BACKUP_MARKET_URLS:
                    logger.info(f"Attempting live cryptocurrency market source ({backup_url})...")
                    try:
                        self.driver.get(backup_url)
                        if "coincodex" in backup_url:
                            self.active_source = "coincodex"
                        elif "yahoo" in backup_url:
                            self.active_source = "yahoo"
                        else:
                            self.active_source = "other"
                        self._handle_cookie_consent()
                        return
                    except TimeoutException:
                        if "coincodex" in backup_url:
                            self.active_source = "coincodex"
                        elif "yahoo" in backup_url:
                            self.active_source = "yahoo"
                        return
                    except Exception as be:
                        logger.warning(f"Source {backup_url} failed: {be}")
                raise RuntimeError("All cryptocurrency market data sources could not be reached.")
            else:
                raise

    def _handle_cookie_consent(self) -> None:
        """Dismisses cookie consent banners if present."""
        try:
            wait = WebDriverWait(self.driver, 2)
            btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.SELECTORS["cookie_accept"]))
            )
            btn.click()
            logger.info("Accepted cookie / privacy dialog.")
        except Exception:
            pass

    def wait_for_data(self, timeout: Optional[int] = None) -> List[WebElement]:
        """
        Explicitly waits for the cryptocurrency table rows to be rendered.
        """
        if self.driver is None:
            raise RuntimeError("Browser not started. Call start_browser() first.")

        wait_timeout = timeout or self.timeout
        logger.info(f"Waiting up to {wait_timeout}s for cryptocurrency data table to load...")

        try:
            wait = WebDriverWait(self.driver, wait_timeout)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
            )
        except TimeoutException:
            # Scroll down and retry locator
            try:
                self.driver.execute_script("window.scrollBy(0, 500);")
            except Exception:
                pass
            wait = WebDriverWait(self.driver, 5)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr, div[class*='table'] div[class*='row']"))
            )

        try:
            self.driver.execute_script("window.scrollBy(0, 500);")
        except Exception:
            pass
        time.sleep(1)

        rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        logger.info(f"Located {len(rows)} cryptocurrency rows from {self.active_source}.")
        return rows

    def parse_coin_row(self, row: WebElement, fallback_rank: int, timestamp: str) -> Optional[CryptoCoin]:
        """
        Parses a single table row WebElement into a validated CryptoCoin dataclass.
        """
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells or len(cells) < 3:
                return None

            raw_cells = [c.text.strip() for c in cells]

            if self.active_source == "coincodex":
                # CoinCodex structure:
                # Cell 0: Rank (e.g. '1')
                # Cell 1: Symbol & Name (e.g. 'BTC | Bitcoin' or 'BTC\nBitcoin')
                # Cell 2: Price (e.g. '$ 84,305')
                # Cell 3: 24h Change (e.g. '0.49%' or '-1.20%')
                # Cell 4: Chart/empty
                # Cell 5: Market Cap (e.g. '$ 1.69T')
                # Cell 6: Volume 24h (e.g. '$ 45.95B')
                rank = parse_rank(raw_cells[0]) or fallback_rank
                name_sym_lines = [l.strip() for l in raw_cells[1].replace("|", "\n").split("\n") if l.strip()]
                if len(name_sym_lines) >= 2:
                    symbol_raw = name_sym_lines[0]
                    name_raw = name_sym_lines[1]
                elif len(name_sym_lines) == 1:
                    symbol_raw = name_sym_lines[0]
                    name_raw = name_sym_lines[0]
                else:
                    symbol_raw = f"COIN{rank}"
                    name_raw = f"Crypto-{rank}"

                price_raw = raw_cells[2] if len(raw_cells) > 2 else None
                change_raw = raw_cells[3] if len(raw_cells) > 3 else None
                mcap_raw = raw_cells[5] if len(raw_cells) > 5 else (raw_cells[4] if len(raw_cells) > 4 else None)
                vol_raw = raw_cells[6] if len(raw_cells) > 6 else (raw_cells[5] if len(raw_cells) > 5 else None)

            elif self.active_source == "yahoo":
                # Yahoo Finance Markets Crypto structure:
                symbol_raw = raw_cells[0].split("\n")[-1].replace("-USD", "").strip()
                if "|" in symbol_raw:
                    symbol_raw = symbol_raw.split("|")[-1].strip()
                name_raw = raw_cells[1].replace(" USD", "").strip() if len(raw_cells) > 1 else symbol_raw
                price_raw = raw_cells[2] if len(raw_cells) > 2 else None
                change_raw = raw_cells[4] if len(raw_cells) > 4 else None
                mcap_raw = raw_cells[5] if len(raw_cells) > 5 else None
                vol_raw = raw_cells[6] if len(raw_cells) > 6 else None
                rank = fallback_rank

            else:
                # CoinMarketCap structure:
                rank_text = raw_cells[1] if len(raw_cells) > 1 else str(fallback_rank)
                rank = parse_rank(rank_text) or fallback_rank

                name_col = cells[2] if len(cells) > 2 else None
                name_text = ""
                symbol_text = ""
                if name_col:
                    lines = [line.strip() for line in name_col.text.split("\n") if line.strip()]
                    if len(lines) >= 2:
                        name_text = lines[0]
                        symbol_text = lines[1]
                    elif len(lines) == 1:
                        name_text = lines[0]
                        symbol_text = lines[0]

                price_raw = raw_cells[3] if len(raw_cells) > 3 else None
                change_raw = None
                for idx in (4, 5, 6):
                    if idx < len(raw_cells) and "%" in raw_cells[idx]:
                        change_raw = raw_cells[idx]
                        break
                mcap_raw = raw_cells[7] if len(raw_cells) > 7 else (raw_cells[6] if len(raw_cells) > 6 else None)
                vol_raw = raw_cells[8] if len(raw_cells) > 8 else None

                name_raw = name_text
                symbol_raw = symbol_text

            parsed_price = parse_currency(price_raw)
            parsed_change = parse_percentage(change_raw)
            parsed_mcap = parse_currency(mcap_raw)
            parsed_volume = parse_volume(vol_raw)

            coin = CryptoCoin(
                rank=rank,
                name=name_raw or f"Crypto-{rank}",
                symbol=symbol_raw or f"COIN{rank}",
                price=parsed_price,
                change_24h=parsed_change,
                market_cap=parsed_mcap,
                volume_24h=parsed_volume,
                timestamp=timestamp,
            )

            validate_coin_data(coin.to_dict())
            return coin

        except Exception as e:
            logger.warning(f"Failed to parse row {fallback_rank}: {e}")
            return None

    def scrape_top_coins(self, limit: int = SCRAPE_LIMIT) -> List[CryptoCoin]:
        """
        Orchestrates full scraping sequence and returns a list of top cryptocurrency objects.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting scraping operation for top {limit} cryptocurrencies at {timestamp}...")

        try:
            self.open_market_page()
            rows = self.wait_for_data()

            coins: List[CryptoCoin] = []
            for idx, row in enumerate(rows):
                if len(coins) >= limit:
                    break
                coin = self.parse_coin_row(row, fallback_rank=idx + 1, timestamp=timestamp)
                if coin is not None:
                    coins.append(coin)

            logger.info(f"Successfully scraped {len(coins)} cryptocurrencies.")
            return coins

        except Exception as e:
            logger.error(f"Error occurred while scraping cryptocurrency market data: {e}")
            raise
        finally:
            self.close_browser()

    def close_browser(self) -> None:
        """Closes the browser session."""
        self.browser_manager.close_driver()
        self.driver = None
