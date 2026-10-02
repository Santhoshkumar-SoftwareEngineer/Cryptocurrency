"""
Cryptocurrency Price Tracker
Main Application Entry Point with interactive CLI and automated scraping modes.
"""
import argparse
import sys
import time
from typing import List, Dict, Any, Optional

from config.settings import (
    SCRAPE_LIMIT,
    SCRAPE_INTERVAL,
    HEADLESS,
    LATEST_CSV_PATH,
    HISTORY_CSV_PATH,
)
from models.crypto import CryptoCoin
from scraper.coinmarketcap import CoinMarketCapScraper
from services.csv_service import (
    save_latest,
    append_history,
    load_latest,
    load_history,
)
from services.filter_service import (
    filter_by_price,
    filter_by_change,
    get_top_gainers,
    get_top_losers,
    search_coin,
)
from services.statistics import calculate_statistics
from services.web_app import create_app
from utils.logger import logger

# Top-level application exports for WSGI, ASGI, and serverless runtimes
app = create_app()
application = app
handler = app


def format_currency_display(val: Optional[float]) -> str:
    """Formats a float as human-readable USD currency."""
    if val is None:
        return "N/A"
    if val >= 1e12:
        return f"${val / 1e12:.2f}T"
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    if val >= 1e6:
        return f"${val / 1e6:.2f}M"
    if val >= 1.0:
        return f"${val:,.2f}"
    return f"${val:.6f}"


def format_change_display(val: Optional[float]) -> str:
    """Formats percentage change with +/- sign."""
    if val is None:
        return "N/A"
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"


def display_coins_table(coins: List[Any], title: Optional[str] = None) -> None:
    """
    Renders a formatted ASCII table of cryptocurrency records.
    """
    if not coins:
        print("\n[INFO] No cryptocurrency records found.\n")
        return

    if title:
        print(f"\n=== {title} ===")

    header_fmt = "{:<6} {:<24} {:<8} {:<15} {:<12} {:<16} {:<16}"
    divider = "-" * 105

    print(divider)
    print(header_fmt.format("Rank", "Coin", "Symbol", "Price", "24h Change", "Market Cap", "24h Volume"))
    print(divider)

    for c in coins:
        # Support both CryptoCoin instances and dict records
        if isinstance(c, CryptoCoin):
            c_dict = c.to_dict()
        else:
            c_dict = c

        rank_str = str(c_dict.get("rank") or "-")
        name_str = (c_dict.get("name") or "Unknown")[:22]
        symbol_str = (c_dict.get("symbol") or "N/A")[:7]
        price_str = format_currency_display(c_dict.get("price"))
        change_str = format_change_display(c_dict.get("change_24h"))
        mcap_str = format_currency_display(c_dict.get("market_cap"))
        vol_str = format_currency_display(c_dict.get("volume_24h"))

        print(header_fmt.format(rank_str, name_str, symbol_str, price_str, change_str, mcap_str, vol_str))

    print(divider)
    print(f"Total: {len(coins)} coin(s)\n")


def display_statistics(stats: Dict[str, Any]) -> None:
    """Prints market summary statistics."""
    print("\n=========================================")
    print("        MARKET SUMMARY STATISTICS        ")
    print("=========================================")
    print(f"Total Coins Tracked : {stats.get('total_coins', 0)}")
    print(f"Data Timestamp      : {stats.get('timestamp') or 'N/A'}")

    avg_ch = stats.get("average_change_24h")
    avg_str = format_change_display(avg_ch) if avg_ch is not None else "N/A"
    print(f"Average 24h Change  : {avg_str}")

    gainer = stats.get("highest_gainer")
    if gainer:
        print(f"Highest 24h Gainer  : {gainer['name']} ({gainer['symbol']}) {format_change_display(gainer.get('change_24h'))} @ {format_currency_display(gainer.get('price'))}")
    else:
        print("Highest 24h Gainer  : N/A")

    loser = stats.get("highest_loser")
    if loser:
        print(f"Highest 24h Loser   : {loser['name']} ({loser['symbol']}) {format_change_display(loser.get('change_24h'))} @ {format_currency_display(loser.get('price'))}")
    else:
        print("Highest 24h Loser   : N/A")

    mcap = stats.get("highest_market_cap")
    if mcap:
        print(f"Highest Market Cap  : {mcap['name']} ({mcap['symbol']}) {format_currency_display(mcap.get('market_cap'))}")
    else:
        print("Highest Market Cap  : N/A")
    print("=========================================\n")


def execute_scrape(limit: int = SCRAPE_LIMIT) -> List[CryptoCoin]:
    """
    Executes a complete scraping workflow and saves to latest and historical CSVs.
    """
    print("\n[INFO] Starting Chrome...")
    print("[INFO] Opening CoinMarketCap...")
    print("[INFO] Waiting for cryptocurrency data...")

    scraper = CoinMarketCapScraper(headless=HEADLESS)
    try:
        coins = scraper.scrape_top_coins(limit=limit)
        if not coins:
            print("[WARNING] No cryptocurrency data was extracted.")
            return []

        print(f"[OK] Scraped {len(coins)} cryptocurrencies")

        save_latest(coins, LATEST_CSV_PATH)
        print("[OK] Latest data saved to data/crypto_latest.csv")

        append_history(coins, HISTORY_CSV_PATH)
        print("[OK] Historical data updated in data/crypto_history.csv")

        return coins
    except Exception as e:
        print(f"[ERROR] Scraping failed: {e}")
        logger.error(f"Scrape execution failed: {e}", exc_info=True)
        return []


def run_once(limit: int = SCRAPE_LIMIT) -> None:
    """Runs a single scrape cycle and displays results."""
    coins = execute_scrape(limit=limit)
    if coins:
        display_coins_table(coins, title="LIVE SCRAPED CRYPTOCURRENCY DATA")
        stats = calculate_statistics(coins)
        display_statistics(stats)


def run_auto(interval: int = SCRAPE_INTERVAL, limit: int = SCRAPE_LIMIT) -> None:
    """Runs automated recurring scraping on a timer."""
    print(f"\n[INFO] Starting Automated Scraping Mode (Interval: {interval}s, Limit: {limit} coins)")
    print("[INFO] Press Ctrl+C at any time to stop.\n")

    iteration = 1
    try:
        while True:
            print(f"\n>>> Scrape Cycle #{iteration} [{time.strftime('%Y-%m-%d %H:%M:%S')}] <<<")
            coins = execute_scrape(limit=limit)
            if coins:
                display_coins_table(coins, title=f"CYCLE #{iteration} SNAPSHOT")
                stats = calculate_statistics(coins)
                display_statistics(stats)

            print(f"[INFO] Sleeping for {interval} seconds until next cycle...")
            time.sleep(interval)
            iteration += 1
    except KeyboardInterrupt:
        print("\n[INFO] Automated scraper stopped by user.")


def interactive_cli() -> None:
    """Runs the interactive command line interface."""
    while True:
        print("=========================================")
        print("       CRYPTOCURRENCY PRICE TRACKER      ")
        print("=========================================")
        print("1. Scrape Top 10 Coins")
        print("2. View Latest Data")
        print("3. View Historical Data")
        print("4. Search Coin")
        print("5. Filter by Price")
        print("6. Filter by 24h Change")
        print("7. Show Top Gainers")
        print("8. Show Top Losers")
        print("9. Show Statistics")
        print("10. Exit")
        print("=========================================")

        try:
            choice = input("Choose an option: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if choice == "1":
            coins = execute_scrape(limit=SCRAPE_LIMIT)
            if coins:
                display_coins_table(coins, title="TOP CRYPTOCURRENCIES")

        elif choice == "2":
            records = load_latest(LATEST_CSV_PATH)
            if records:
                display_coins_table(records, title="LATEST SAVED CRYPTOCURRENCY DATA")
            else:
                print("\n[WARNING] No latest data found. Run Option 1 to scrape first.\n")

        elif choice == "3":
            records = load_history(HISTORY_CSV_PATH)
            if records:
                # Show last 20 historical entries by default for readability
                display_coins_table(records[-20:], title=f"HISTORICAL CRYPTOCURRENCY DATA (Showing last {min(20, len(records))} records)")
            else:
                print("\n[WARNING] No historical data found. Run Option 1 to scrape first.\n")

        elif choice == "4":
            records = load_latest(LATEST_CSV_PATH)
            if not records:
                print("\n[WARNING] No data available to search. Please scrape first (Option 1).\n")
                continue
            query = input("Enter coin name or symbol to search: ").strip()
            results = search_coin(records, query)
            display_coins_table(results, title=f"SEARCH RESULTS FOR '{query}'")

        elif choice == "5":
            records = load_latest(LATEST_CSV_PATH)
            if not records:
                print("\n[WARNING] No data available to filter. Please scrape first (Option 1).\n")
                continue
            try:
                min_p_input = input("Enter minimum price in USD (or press Enter to skip): ").strip()
                max_p_input = input("Enter maximum price in USD (or press Enter to skip): ").strip()
                min_p = float(min_p_input) if min_p_input else None
                max_p = float(max_p_input) if max_p_input else None
                results = filter_by_price(records, min_price=min_p, max_price=max_p)
                display_coins_table(results, title="PRICE FILTERED RESULTS")
            except ValueError:
                print("\n[ERROR] Invalid price input. Please enter numeric values.\n")

        elif choice == "6":
            records = load_latest(LATEST_CSV_PATH)
            if not records:
                print("\n[WARNING] No data available to filter. Please scrape first (Option 1).\n")
                continue
            try:
                min_c_input = input("Enter minimum 24h percentage change (e.g. -2.0, or Enter to skip): ").strip()
                max_c_input = input("Enter maximum 24h percentage change (e.g. 5.0, or Enter to skip): ").strip()
                min_c = float(min_c_input) if min_c_input else None
                max_c = float(max_c_input) if max_c_input else None
                results = filter_by_change(records, min_change=min_c, max_change=max_c)
                display_coins_table(results, title="24H CHANGE FILTERED RESULTS")
            except ValueError:
                print("\n[ERROR] Invalid percentage input. Please enter numeric values.\n")

        elif choice == "7":
            records = load_latest(LATEST_CSV_PATH)
            if not records:
                print("\n[WARNING] No data available. Please scrape first (Option 1).\n")
                continue
            top_gainers = get_top_gainers(records, count=5)
            display_coins_table(top_gainers, title="TOP 5 24H GAINERS")

        elif choice == "8":
            records = load_latest(LATEST_CSV_PATH)
            if not records:
                print("\n[WARNING] No data available. Please scrape first (Option 1).\n")
                continue
            top_losers = get_top_losers(records, count=5)
            display_coins_table(top_losers, title="TOP 5 24H LOSERS")

        elif choice == "9":
            records = load_latest(LATEST_CSV_PATH)
            if not records:
                print("\n[WARNING] No data available. Please scrape first (Option 1).\n")
                continue
            stats = calculate_statistics(records)
            display_statistics(stats)

        elif choice == "10":
            print("\nThank you for using Cryptocurrency Price Tracker. Goodbye!\n")
            break

        else:
            print("\n[ERROR] Invalid option. Please enter a number between 1 and 10.\n")


def run_web_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Runs the built-in HTTP development server."""
    from wsgiref.simple_server import make_server
    print("\n=========================================")
    print("   CRYPTOPULSE WEB SERVER RUNNING")
    print("=========================================")
    print(f" URL: http://{host}:{port}/")
    print(f" API: http://{host}:{port}/api/latest")
    print(" Press Ctrl+C to stop the server.")
    print("=========================================\n")
    try:
        with make_server(host, port, app) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Web server stopped.")


def main() -> None:
    """Main CLI parser and dispatcher."""
    parser = argparse.ArgumentParser(
        description="Cryptocurrency Price Tracker - Live Automated Market Data Scraper"
    )
    parser.add_argument(
        "--web",
        "--server",
        action="store_true",
        help="Launch the real-time web dashboard and REST API server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the web server to (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind the web server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Execute a single scraping cycle, persist data to CSV, display results, and exit.",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run continuously in automated recurring mode at configured intervals.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=SCRAPE_LIMIT,
        help=f"Number of top cryptocurrencies to scrape (default: {SCRAPE_LIMIT})",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=SCRAPE_INTERVAL,
        help=f"Interval in seconds between automated scrape cycles (default: {SCRAPE_INTERVAL}s)",
    )

    args = parser.parse_args()

    if args.web:
        run_web_server(host=args.host, port=args.port)
    elif args.once:
        run_once(limit=args.limit)
    elif args.auto:
        run_auto(interval=args.interval, limit=args.limit)
    else:
        interactive_cli()


if __name__ == "__main__":
    main()
