"""Scraper package for cryptocurrency market data extraction."""
from .browser import BrowserManager
from .coinmarketcap import CoinMarketCapScraper

__all__ = ["BrowserManager", "CoinMarketCapScraper"]
