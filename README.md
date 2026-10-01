# Cryptocurrency Price Tracker

A production-quality Python automation and data engineering tool that uses **Selenium WebDriver** to dynamically scrape live cryptocurrency market data from CoinMarketCap (and real-time market mirrors), process numerical values with data validation, and store persistent snapshots and historical records in CSV format.

---

## Features

- **Dynamic Web Scraping**: Automates Chrome using Selenium to render JavaScript heavy cryptocurrency listings and extract live market metrics (Rank, Coin Name, Symbol, Live Price, 24h Percentage Change, Market Cap, and 24h Volume).
- **Explicit Waits & Robust Locators**: Utilizes `WebDriverWait` and resilient CSS/XPath selectors to gracefully handle page rendering and dynamic DOM updates without excessive hardcoded sleeps.
- **Configurable Browser Automation**: Supports headless mode, configurable window sizes, and automated ChromeDriver management via `webdriver-manager` and Selenium Manager.
- **Dual CSV Storage**:
  - `data/crypto_latest.csv`: Overwritten with the most recent scraping snapshot.
  - `data/crypto_history.csv`: Appended on every run with timestamped records for trend analysis.
- **Advanced Filtering & Search**:
  - Filter by minimum and maximum price.
  - Filter by 24-hour percentage gain/loss thresholds.
  - View Top 5 24h Gainers and Losers.
  - Search coins by name or ticker symbol.
- **Market Summary Statistics**: Calculates total coins tracked, top gainer, top loser, largest market cap, and average 24-hour market change.
- **Automated Recurring Mode**: Run continuous scraping cycles at configurable intervals (`--auto`).
- **Resilient Fallback**: Automatically recovers from network connection resets or ISP regional blocks by falling back to live market mirrors without using fake or hardcoded data.
- **Comprehensive Logging**: Detailed execution logs written to `logs/app.log`.

---

## Technologies

- **Python 3.11+**
- **Selenium 4+** (Browser Automation)
- **webdriver-manager** (Automatic Driver Lifecycle Management)
- **pandas** (Data Processing & CSV persistence)
- **python-dotenv** (Environment Configuration)
- **pytest** (Comprehensive Test Suite)

---

## Project Structure

```
Crypto project/
│
├── main.py                     # Application entry point & interactive CLI
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
├── .env.example                # Example environment variable file
├── .env                        # Active environment configuration
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Environment loader & global configuration
│
├── scraper/
│   ├── __init__.py
│   ├── browser.py              # Chrome WebDriver manager & options
│   └── coinmarketcap.py        # Live market scraper & DOM parser
│
├── models/
│   ├── __init__.py
│   └── crypto.py               # CryptoCoin dataclass model
│
├── services/
│   ├── __init__.py
│   ├── csv_service.py          # CSV persistence & history logging
│   ├── filter_service.py       # Filtering, sorting, and search logic
│   └── statistics.py           # Summary statistics calculations
│
├── utils/
│   ├── __init__.py
│   ├── logger.py               # Centralized file and console logger
│   ├── parser.py               # String, currency, & percentage cleaner
│   └── validators.py           # Data schema & model validation
│
├── data/
│   ├── .gitkeep
│   ├── crypto_latest.csv       # Latest scrape snapshot
│   └── crypto_history.csv      # Continuous historical log
│
├── logs/
│   ├── .gitkeep
│   └── app.log                 # Execution logs
│
└── tests/
    ├── __init__.py
    ├── test_parser.py          # Unit tests for string & numeric parsers
    ├── test_filters.py         # Unit tests for filter and search services
    ├── test_statistics.py      # Unit tests for statistical calculations
    └── test_csv_service.py     # Unit tests for CSV persistence operations
```

---

## Installation (Windows PowerShell)

1. Clone or open the project folder:
   ```powershell
   cd "Crypto project"
   ```

2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install project dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Create your `.env` configuration file:
   ```powershell
   Copy-Item .env.example .env
   ```

---

## Configuration

Settings are configured via `.env`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `HEADLESS` | `true` | Runs Chrome in headless background mode (`true`/`false`) |
| `WINDOW_SIZE` | `1920,1080` | Browser viewport dimensions |
| `SCRAPE_LIMIT` | `10` | Number of top coins to scrape |
| `SCRAPE_INTERVAL` | `300` | Seconds to wait between automated recurring cycles |
| `PAGE_TIMEOUT` | `25` | Maximum wait time (seconds) for page loading |
| `COINMARKETCAP_URL` | `https://coinmarketcap.com/` | Primary scraping target URL |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Running the Application

### 1. Interactive CLI Mode
Run the interactive console menu:
```powershell
python main.py
```

Menu options:
```
=========================================
       CRYPTOCURRENCY PRICE TRACKER      
=========================================
1. Scrape Top 10 Coins
2. View Latest Data
3. View Historical Data
4. Search Coin
5. Filter by Price
6. Filter by 24h Change
7. Show Top Gainers
8. Show Top Losers
9. Show Statistics
10. Exit
=========================================
```

### 2. Single Run Mode (`--once`)
Executes a single live scraping cycle, persists results to CSV files, prints formatted output and market statistics, and exits:
```powershell
python main.py --once
```

### 3. Automated Recurring Mode (`--auto`)
Runs continuously at configured intervals (e.g. every 300 seconds), periodically updating `data/crypto_latest.csv` and appending records to `data/crypto_history.csv`:
```powershell
python main.py --auto
```
*Optional flags:*
- `--limit 10`: Specify number of top coins.
- `--interval 60`: Set custom interval in seconds.

---

## Output Data

### 1. `data/crypto_latest.csv`
Overwritten on every scrape cycle with the freshest market data.

**Columns:**
`timestamp`, `rank`, `name`, `symbol`, `price`, `change_24h`, `market_cap`, `volume_24h`

### 2. `data/crypto_history.csv`
Appends each new scrape cycle with timestamped entries to maintain long-term price history.

---

## Example Output

```
=== LIVE SCRAPED CRYPTOCURRENCY DATA ===
---------------------------------------------------------------------------------------------------------
Rank   Coin                     Symbol   Price           24h Change   Market Cap       24h Volume      
---------------------------------------------------------------------------------------------------------
1      Bitcoin                  BTC      $83,847.00      -0.46%       $1.68T           $35.55B         
2      Ethereum                 ETH      $2,674.51       -0.40%       $326.55B         $30.13B         
3      Tether                   USDT     $0.999600       +0.03%       $183.79B         $140.02B        
4      Binance Coin             BNB      $765.17         -0.44%       $101.89B         $1.69B          
5      XRP                      XRP      $1.48           -1.50%       $93.41B          $3.33B          
6      USD Coin                 USDC     $0.999900       0.00%        $74.15B          $25.38B         
7      Solana                   SOL      $117.21         -1.61%       $68.92B          $6.46B          
8      TRON                     TRX      $0.333900       -1.47%       $31.69B          $603.59M        
9      Zcash                    ZEC      $1,371.72       -4.21%       $23.18B          $3.26B          
10     Hyperliquid              HYPE     $87.96          +2.00%       $22.08B          $2.20B          
---------------------------------------------------------------------------------------------------------
Total: 10 coin(s)

=========================================
        MARKET SUMMARY STATISTICS        
=========================================
Total Coins Tracked : 10
Data Timestamp      : 2026-10-01 21:10:22
Average 24h Change  : -0.81%
Highest 24h Gainer  : Hyperliquid (HYPE) +2.00% @ $87.96
Highest 24h Loser   : Zcash (ZEC) -4.21% @ $1,371.72
Highest Market Cap  : Bitcoin (BTC) $1.68T
=========================================
```

---

## Running Unit Tests

Run all unit tests using pytest:
```powershell
python -m pytest -v
```

All 18 unit tests cover:
1. `test_parser.py`: Currency strings (`$67,000.50`, `$1.3T`, `$850M`, `$25.4B`), percentages (`+2.35%`, `-1.5%`), ranks, and market caps.
2. `test_filters.py`: Price boundaries, percentage change filtering, top gainers, top losers, and name/symbol search.
3. `test_statistics.py`: Aggregations, mean calculations, top gainer/loser identification, and empty/null handling.
4. `test_csv_service.py`: Snapshot overwrites and historical appends.

---

## Troubleshooting

1. **Chrome / ChromeDriver mismatch**:
   - The application leverages Selenium 4's built-in driver manager and `webdriver-manager` to automatically download and match the correct ChromeDriver for your installed Google Chrome browser.
2. **Network / Regional Restrictions**:
   - In regions where certain cryptocurrency domains (such as `coinmarketcap.com`) are restricted or blocked at the ISP DNS level, the scraper automatically routes to verified live market sources (`coincodex.com` / Yahoo Finance Crypto) so that live data is continuously available without interruption.
3. **Headless Mode**:
   - If you want to visually observe the browser in action, set `HEADLESS=false` in `.env`.
