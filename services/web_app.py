"""
Cryptocurrency Price Tracker - Web Application & API Service.
Provides a modern, responsive web dashboard and REST API endpoints.
Implements a dual WSGI & ASGI compatible application interface (app, application, handler).
"""
import json
import urllib.parse
from typing import Dict, Any, List, Optional
from datetime import datetime

from config.settings import LATEST_CSV_PATH, HISTORY_CSV_PATH, SCRAPE_LIMIT
from scraper.coinmarketcap import CoinMarketCapScraper
from services.csv_service import load_latest, load_history, save_latest, append_history
from services.statistics import calculate_statistics
from utils.logger import logger


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CryptoPulse | Real-Time Cryptocurrency Price Tracker</title>
  <meta name="description" content="Live Cryptocurrency Price Tracker and Market Intelligence Dashboard with automated real-time web scraping.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #0a0e17;
      --bg-secondary: #111827;
      --bg-card: rgba(17, 24, 39, 0.75);
      --bg-card-hover: rgba(31, 41, 55, 0.85);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(59, 130, 246, 0.3);
      --text-primary: #f9fafb;
      --text-secondary: #9ca3af;
      --text-muted: #6b7280;
      --accent-blue: #3b82f6;
      --accent-cyan: #06b6d4;
      --accent-purple: #8b5cf6;
      --accent-green: #10b981;
      --accent-green-bg: rgba(16, 185, 129, 0.15);
      --accent-red: #ef4444;
      --accent-red-bg: rgba(239, 68, 68, 0.15);
      --gradient-accent: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06b6d4 100%);
      --gradient-card: linear-gradient(180deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
      --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
      --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 20px rgba(59, 130, 246, 0.15);
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(59, 130, 246, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 85% 25%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 80%, rgba(6, 182, 212, 0.05) 0%, transparent 50%);
      background-attachment: fixed;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px 20px 60px;
    }

    /* Header */
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      margin-bottom: 28px;
      box-shadow: var(--shadow-sm);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .logo-icon {
      width: 44px;
      height: 44px;
      border-radius: var(--radius-md);
      background: var(--gradient-accent);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }

    .brand-text h1 {
      font-size: 22px;
      font-weight: 700;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -0.5px;
    }

    .brand-text p {
      font-size: 13px;
      color: var(--text-secondary);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .live-dot {
      width: 8px;
      height: 8px;
      background-color: var(--accent-green);
      border-radius: 50%;
      display: inline-block;
      box-shadow: 0 0 10px var(--accent-green);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 14px var(--accent-green); }
      100% { transform: scale(0.95); opacity: 0.8; }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 18px;
      font-size: 14px;
      font-weight: 600;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
      font-family: inherit;
      text-decoration: none;
    }

    .btn-primary {
      background: var(--gradient-accent);
      color: white;
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.35);
    }

    .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
    }

    .btn-primary:active {
      transform: translateY(0);
    }

    .btn-secondary {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.15);
    }

    /* Stats Grid */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px;
      margin-bottom: 28px;
    }

    .stat-card {
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 20px;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .stat-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--gradient-accent);
      opacity: 0.6;
    }

    .stat-card:hover {
      transform: translateY(-3px);
      border-color: var(--border-glow);
    }

    .stat-title {
      font-size: 13px;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .stat-value {
      font-size: 24px;
      font-weight: 700;
      color: var(--text-primary);
      font-family: 'JetBrains Mono', monospace;
    }

    .stat-subtitle {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 6px;
    }

    /* Controls & Filters Bar */
    .controls-bar {
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 18px 22px;
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .search-box {
      flex: 1;
      min-width: 240px;
      position: relative;
    }

    .search-input {
      width: 100%;
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 10px 16px 10px 40px;
      color: var(--text-primary);
      font-size: 14px;
      font-family: inherit;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .search-input:focus {
      border-color: var(--accent-blue);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }

    .search-icon {
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 15px;
    }

    .filter-tags {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .filter-btn {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-color);
      color: var(--text-secondary);
      padding: 8px 14px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      font-family: inherit;
    }

    .filter-btn:hover, .filter-btn.active {
      background: rgba(59, 130, 246, 0.15);
      color: #93c5fd;
      border-color: rgba(59, 130, 246, 0.4);
    }

    /* Table Container */
    .table-container {
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      overflow: hidden;
      box-shadow: var(--shadow-lg);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
    }

    thead {
      background: rgba(0, 0, 0, 0.35);
      border-bottom: 1px solid var(--border-color);
    }

    th {
      padding: 16px 20px;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      user-select: none;
    }

    tbody tr {
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      transition: background 0.15s ease;
    }

    tbody tr:last-child {
      border-bottom: none;
    }

    tbody tr:hover {
      background: var(--bg-card-hover);
    }

    td {
      padding: 16px 20px;
      font-size: 14px;
      vertical-align: middle;
    }

    .coin-cell {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .coin-badge {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.06);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 11px;
      color: #cbd5e1;
      border: 1px solid var(--border-color);
    }

    .coin-name {
      font-weight: 600;
      color: var(--text-primary);
    }

    .coin-symbol {
      font-size: 12px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }

    .price-cell {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      color: var(--text-primary);
    }

    .badge-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }

    .badge-gain {
      color: var(--accent-green);
      background: var(--accent-green-bg);
      border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .badge-loss {
      color: var(--accent-red);
      background: var(--accent-red-bg);
      border: 1px solid rgba(239, 68, 68, 0.25);
    }

    .badge-neutral {
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-color);
    }

    .mcap-cell, .vol-cell {
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-secondary);
    }

    /* Modal */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(8px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }

    .modal-card {
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      width: 100%;
      max-width: 900px;
      max-height: 80vh;
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-lg);
    }

    .modal-header {
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .modal-body {
      padding: 20px 24px;
      overflow-y: auto;
    }

    .close-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-size: 20px;
      cursor: pointer;
    }
    .close-btn:hover { color: var(--text-primary); }

    /* Footer */
    footer {
      margin-top: 40px;
      text-align: center;
      color: var(--text-muted);
      font-size: 13px;
    }

    /* Toast Notification */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--bg-secondary);
      border: 1px solid var(--accent-blue);
      box-shadow: var(--shadow-lg);
      padding: 14px 20px;
      border-radius: var(--radius-md);
      color: white;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      z-index: 2000;
    }

    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }

    .spinner {
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      display: inline-block;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    @media (max-width: 768px) {
      header { flex-direction: column; gap: 16px; align-items: flex-start; }
      .header-actions { width: 100%; justify-content: space-between; }
      .controls-bar { flex-direction: column; align-items: stretch; }
      th:nth-child(6), td:nth-child(6), th:nth-child(7), td:nth-child(7) { display: none; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        <div class="logo-icon">⚡</div>
        <div class="brand-text">
          <h1>CryptoPulse Tracker</h1>
          <p><span class="live-dot"></span> Live Market Intelligence Engine</p>
        </div>
      </div>
      <div class="header-actions">
        <button id="scrapeBtn" class="btn btn-primary" onclick="triggerScrape()">
          <span id="scrapeIcon">⚡</span> <span id="scrapeText">Scrape Live Data</span>
        </button>
        <button class="btn btn-secondary" onclick="openHistoryModal()">
          📜 View History
        </button>
      </div>
    </header>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-title">Tracked Cryptos <span>🌐</span></div>
        <div class="stat-value" id="statCount">--</div>
        <div class="stat-subtitle" id="statTimestamp">Last updated: --</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Market 24h Trend <span>📊</span></div>
        <div class="stat-value" id="statAvgChange">--</div>
        <div class="stat-subtitle">Average 24h Change</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Top 24h Gainer <span>🚀</span></div>
        <div class="stat-value" id="statTopGainer" style="color: var(--accent-green); font-size: 20px;">--</div>
        <div class="stat-subtitle" id="statTopGainerSub">--</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Top 24h Loser <span>🔻</span></div>
        <div class="stat-value" id="statTopLoser" style="color: var(--accent-red); font-size: 20px;">--</div>
        <div class="stat-subtitle" id="statTopLoserSub">--</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">Market Dominance <span>👑</span></div>
        <div class="stat-value" id="statDominance" style="font-size: 20px;">--</div>
        <div class="stat-subtitle" id="statDominanceSub">Highest Market Cap</div>
      </div>
    </div>

    <!-- Controls Bar -->
    <div class="controls-bar">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Search by coin name or symbol (e.g. BTC, Ethereum)..." oninput="filterData()">
      </div>
      <div class="filter-tags">
        <button class="filter-btn active" data-filter="all" onclick="setFilter('all')">All Coins</button>
        <button class="filter-btn" data-filter="gainers" onclick="setFilter('gainers')">🔥 Top Gainers</button>
        <button class="filter-btn" data-filter="losers" onclick="setFilter('losers')">📉 Top Losers</button>
        <button class="filter-btn" data-filter="largecap" onclick="setFilter('largecap')">💎 >$10B Cap</button>
      </div>
    </div>

    <!-- Table Container -->
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th style="width: 70px;">Rank</th>
            <th>Name</th>
            <th>Price</th>
            <th>24h Change</th>
            <th>Market Cap</th>
            <th>24h Volume</th>
          </tr>
        </thead>
        <tbody id="coinsTableBody">
          <tr>
            <td colspan="6" style="text-align:center; padding: 40px; color: var(--text-muted);">
              <div class="spinner"></div> Loading cryptocurrency assets...
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <footer>
      <p>CryptoPulse Automation Engine • Powered by Selenium & Real-time Scraper • Dual WSGI/ASGI Interface</p>
    </footer>
  </div>

  <!-- History Modal -->
  <div id="historyModal" class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <h2 style="font-size: 18px; font-weight: 700;">📜 Historical Scrape Records</h2>
        <button class="close-btn" onclick="closeHistoryModal()">&times;</button>
      </div>
      <div class="modal-body">
        <table style="width: 100%;">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Rank</th>
              <th>Coin</th>
              <th>Price</th>
              <th>24h Change</th>
            </tr>
          </thead>
          <tbody id="historyTableBody">
            <tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Loading historical records...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div id="toast" class="toast">
    <span id="toastIcon">ℹ️</span>
    <span id="toastMsg">Notification message</span>
  </div>

  <script>
    let allCoins = [];
    let currentFilter = 'all';

    function formatCurrency(val) {
      if (val === null || val === undefined || isNaN(val)) return 'N/A';
      if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`;
      if (val >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
      if (val >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
      if (val >= 1.0) return `$${Number(val).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
      return `$${Number(val).toFixed(6)}`;
    }

    function formatPercent(val) {
      if (val === null || val === undefined || isNaN(val)) return 'N/A';
      const sign = val > 0 ? '+' : '';
      return `${sign}${val.toFixed(2)}%`;
    }

    function showToast(msg, icon = 'ℹ️') {
      const toast = document.getElementById('toast');
      document.getElementById('toastMsg').innerText = msg;
      document.getElementById('toastIcon').innerText = icon;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 3500);
    }

    async function loadData() {
      try {
        const [coinsRes, statsRes] = await Promise.all([
          fetch('/api/latest'),
          fetch('/api/stats')
        ]);
        allCoins = await coinsRes.json();
        const stats = await statsRes.json();
        
        updateStatsUI(stats);
        filterData();
      } catch (err) {
        console.error('Error loading data:', err);
        document.getElementById('coinsTableBody').innerHTML = `
          <tr><td colspan="6" style="text-align:center; padding: 30px; color: var(--accent-red);">
            Failed to load market data. Try triggering a live scrape!
          </td></tr>
        `;
      }
    }

    function updateStatsUI(stats) {
      document.getElementById('statCount').innerText = stats.total_coins || allCoins.length || '0';
      document.getElementById('statTimestamp').innerText = `Updated: ${stats.timestamp || 'Just now'}`;
      
      const avg = stats.avg_change_24h;
      const avgEl = document.getElementById('statAvgChange');
      if (avg !== undefined && avg !== null) {
        avgEl.innerText = formatPercent(avg);
        avgEl.style.color = avg >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
      }

      if (stats.top_gainer) {
        document.getElementById('statTopGainer').innerText = `${stats.top_gainer.symbol || ''} ${formatPercent(stats.top_gainer.change_24h)}`;
        document.getElementById('statTopGainerSub').innerText = `${stats.top_gainer.name} @ ${formatCurrency(stats.top_gainer.price)}`;
      } else {
        document.getElementById('statTopGainer').innerText = '--';
        document.getElementById('statTopGainerSub').innerText = '--';
      }

      if (stats.top_loser) {
        document.getElementById('statTopLoser').innerText = `${stats.top_loser.symbol || ''} ${formatPercent(stats.top_loser.change_24h)}`;
        document.getElementById('statTopLoserSub').innerText = `${stats.top_loser.name} @ ${formatCurrency(stats.top_loser.price)}`;
      } else {
        document.getElementById('statTopLoser').innerText = '--';
        document.getElementById('statTopLoserSub').innerText = '--';
      }

      if (stats.largest_market_cap) {
        document.getElementById('statDominance').innerText = stats.largest_market_cap.symbol || '--';
        document.getElementById('statDominanceSub').innerText = `${formatCurrency(stats.largest_market_cap.market_cap)} Cap`;
      }
    }

    function setFilter(type) {
      currentFilter = type;
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.filter === type);
      });
      filterData();
    }

    function filterData() {
      const q = document.getElementById('searchInput').value.trim().toLowerCase();
      let list = [...allCoins];

      if (q) {
        list = list.filter(c => 
          (c.name && c.name.toLowerCase().includes(q)) || 
          (c.symbol && c.symbol.toLowerCase().includes(q))
        );
      }

      if (currentFilter === 'gainers') {
        list = list.filter(c => (c.change_24h || 0) > 0).sort((a,b) => (b.change_24h||0) - (a.change_24h||0));
      } else if (currentFilter === 'losers') {
        list = list.filter(c => (c.change_24h || 0) < 0).sort((a,b) => (a.change_24h||0) - (b.change_24h||0));
      } else if (currentFilter === 'largecap') {
        list = list.filter(c => (c.market_cap || 0) >= 1e10);
      }

      renderTable(list);
    }

    function renderTable(coins) {
      const tbody = document.getElementById('coinsTableBody');
      if (!coins || coins.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 30px; color: var(--text-muted);">No cryptocurrencies match your criteria.</td></tr>`;
        return;
      }

      tbody.innerHTML = coins.map(c => {
        const ch = c.change_24h;
        let badgeClass = 'badge-neutral';
        let badgeSign = '';
        if (ch > 0) {
          badgeClass = 'badge-gain';
          badgeSign = '+';
        } else if (ch < 0) {
          badgeClass = 'badge-loss';
        }

        return `
          <tr>
            <td style="font-family: 'JetBrains Mono', monospace; font-weight: 600; color: var(--text-muted);">${c.rank || '-'}</td>
            <td>
              <div class="coin-cell">
                <div class="coin-badge">${(c.symbol || 'C').substring(0, 3).toUpperCase()}</div>
                <div>
                  <div class="coin-name">${c.name || 'Unknown'}</div>
                  <div class="coin-symbol">${c.symbol || ''}</div>
                </div>
              </div>
            </td>
            <td class="price-cell">${formatCurrency(c.price)}</td>
            <td>
              <span class="badge-pill ${badgeClass}">
                ${ch !== null && ch !== undefined ? `${badgeSign}${ch.toFixed(2)}%` : 'N/A'}
              </span>
            </td>
            <td class="mcap-cell">${formatCurrency(c.market_cap)}</td>
            <td class="vol-cell">${formatCurrency(c.volume_24h)}</td>
          </tr>
        `;
      }).join('');
    }

    async function triggerScrape() {
      const btn = document.getElementById('scrapeBtn');
      const text = document.getElementById('scrapeText');
      const icon = document.getElementById('scrapeIcon');

      btn.disabled = true;
      icon.innerHTML = '<span class="spinner"></span>';
      text.innerText = 'Scraping Live Markets...';
      showToast('Automating browser & scraping CoinMarketCap...', '⏳');

      try {
        const res = await fetch('/api/scrape', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast(`Successfully scraped ${data.coins ? data.coins.length : 10} coins!`, '✅');
          await loadData();
        } else {
          showToast('Scraping error: ' + (data.error || 'Unknown'), '⚠️');
        }
      } catch (e) {
        showToast('Scrape request failed: ' + e.message, '❌');
      } finally {
        btn.disabled = false;
        icon.innerHTML = '⚡';
        text.innerText = 'Scrape Live Data';
      }
    }

    async function openHistoryModal() {
      document.getElementById('historyModal').style.display = 'flex';
      const tbody = document.getElementById('historyTableBody');
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);"><span class="spinner"></span> Loading historical logs...</td></tr>';
      
      try {
        const res = await fetch('/api/history');
        const history = await res.json();
        if (!history || history.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No history recorded yet.</td></tr>';
          return;
        }

        tbody.innerHTML = history.slice(-50).reverse().map(h => `
          <tr>
            <td style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-muted);">${h.timestamp || '-'}</td>
            <td style="font-family: 'JetBrains Mono', monospace;">${h.rank || '-'}</td>
            <td style="font-weight: 600;">${h.name} <span style="font-size:12px; color:var(--text-muted)">(${h.symbol})</span></td>
            <td style="font-family: 'JetBrains Mono', monospace;">${formatCurrency(h.price)}</td>
            <td>
              <span class="badge-pill ${(h.change_24h > 0) ? 'badge-gain' : ((h.change_24h < 0) ? 'badge-loss' : 'badge-neutral')}">
                ${formatPercent(h.change_24h)}
              </span>
            </td>
          </tr>
        `).join('');
      } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--accent-red);">Failed to load history: ${e.message}</td></tr>`;
      }
    }

    function closeHistoryModal() {
      document.getElementById('historyModal').style.display = 'none';
    }

    // Auto-load on startup
    loadData();
    // Auto-refresh UI every 30s
    setInterval(loadData, 30000);
  </script>
</body>
</html>
"""


class CryptoWebApp:
    """
    Universal WSGI & ASGI compatible Web Application.
    Exposes REST API endpoints and dashboard UI for Cryptocurrency Price Tracker.
    """

    def handle_request(self, path: str, method: str) -> tuple[int, str, bytes]:
        """Core routing logic returning (status_code, content_type, body_bytes)."""
        clean_path = path.split("?")[0].rstrip("/") or "/"
        
        if clean_path == "/" or clean_path == "/index.html":
            return 200, "text/html; charset=utf-8", HTML_TEMPLATE.encode("utf-8")

        elif clean_path == "/api/latest":
            records = load_latest(LATEST_CSV_PATH)
            # If no CSV records exist, scrape once automatically
            if not records:
                try:
                    scraper = CoinMarketCapScraper(headless=True)
                    coins = scraper.scrape_top_coins(limit=SCRAPE_LIMIT)
                    if coins:
                        save_latest(coins)
                        append_history(coins)
                        records = [c.to_dict() for c in coins]
                except Exception as e:
                    logger.error(f"Auto-scrape in /api/latest failed: {e}")
                    records = []
            return 200, "application/json", json.dumps(records, default=str).encode("utf-8")

        elif clean_path == "/api/history":
            history = load_history(HISTORY_CSV_PATH)
            return 200, "application/json", json.dumps(history, default=str).encode("utf-8")

        elif clean_path == "/api/stats":
            records = load_latest(LATEST_CSV_PATH)
            stats = calculate_statistics(records)
            return 200, "application/json", json.dumps(stats, default=str).encode("utf-8")

        elif clean_path == "/api/scrape":
            if method.upper() in ["POST", "GET"]:
                try:
                    scraper = CoinMarketCapScraper(headless=True)
                    coins = scraper.scrape_top_coins(limit=SCRAPE_LIMIT)
                    if coins:
                        save_latest(coins)
                        append_history(coins)
                        coin_dicts = [c.to_dict() for c in coins]
                        return 200, "application/json", json.dumps({"success": True, "coins": coin_dicts}, default=str).encode("utf-8")
                    else:
                        return 500, "application/json", json.dumps({"success": False, "error": "No coins returned from scraper"}).encode("utf-8")
                except Exception as e:
                    logger.error(f"Error during on-demand scrape: {e}")
                    return 500, "application/json", json.dumps({"success": False, "error": str(e)}).encode("utf-8")
            else:
                return 405, "application/json", json.dumps({"error": "Method Not Allowed"}).encode("utf-8")

        return 404, "application/json", json.dumps({"error": "Not Found"}).encode("utf-8")

    def __call__(self, *args, **kwargs):
        """
        Dispatches dynamically to WSGI or ASGI interface:
        - WSGI: (environ, start_response)
        - ASGI: (scope, receive, send)
        """
        if len(args) == 2 and callable(args[1]):
            # WSGI mode
            environ, start_response = args
            path = environ.get("PATH_INFO", "/")
            method = environ.get("REQUEST_METHOD", "GET")
            status_code, content_type, body = self.handle_request(path, method)

            status_text = {
                200: "200 OK",
                404: "404 Not Found",
                405: "405 Method Not Allowed",
                500: "500 Internal Server Error",
            }.get(status_code, f"{status_code} Status")

            headers = [
                ("Content-Type", content_type),
                ("Content-Length", str(len(body))),
                ("Access-Control-Allow-Origin", "*"),
                ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                ("Access-Control-Allow-Headers", "Content-Type"),
            ]
            start_response(status_text, headers)
            return [body]

        elif len(args) == 3:
            # ASGI mode
            scope, receive, send = args
            return self._asgi_call(scope, receive, send)

        raise TypeError("CryptoWebApp must be invoked as WSGI or ASGI application.")

    async def _asgi_call(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "/")
            method = scope.get("method", "GET")
            status_code, content_type, body = self.handle_request(path, method)

            await send({
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", content_type.encode("utf-8")),
                    (b"content-length", str(len(body)).encode("utf-8")),
                    (b"access-control-allow-origin", b"*"),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
        elif scope["type"] == "lifespan":
            while True:
                message = await receive()
                if message["type"] == "lifespan.startup":
                    await send({"type": "lifespan.startup.complete"})
                elif message["type"] == "lifespan.shutdown":
                    await send({"type": "lifespan.shutdown.complete"})
                    break


def create_app() -> CryptoWebApp:
    """Factory function creating the web application instance."""
    return CryptoWebApp()
