# Stock Analysis System

A terminal-based stock analysis tool with technical indicators, ASCII charting, and portfolio tracking.

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Stock Quote & Info** | Company details, sector, P/E, dividend yield, 52-week range |
| 2 | **Price Chart** | ASCII closing-price chart in the terminal |
| 3 | **Technical Analysis** | SMA, EMA, RSI, MACD, Bollinger Bands with buy/sell signals |
| 4 | **Full Report** | Combined info + chart + signals in one view |
| 5 | **Portfolio View** | Track holdings with live P&L |
| 6 | **Portfolio Add** | Add positions with cost basis |
| 7 | **Portfolio Remove** | Remove positions |
| 8 | **Compare Stocks** | Side-by-side comparison of multiple tickers |

## Data Modes

- **Live mode**: When internet is available, fetches real data from Yahoo Finance via `yfinance`.
- **Sample mode**: When offline, generates realistic simulated data for 10 pre-configured tickers (AAPL, MSFT, GOOG, AMZN, TSLA, NVDA, JPM, JNJ, V, WMT) plus any custom symbol.

## Project Structure

```
run.py                          # Entry point
requirements.txt                # Python dependencies
stock_analysis/
  __init__.py
  cli.py                        # Interactive menu CLI
  data.py                       # Data fetching (live + sample fallback)
  sample_data.py                # Sample data generator
  indicators.py                 # Technical indicators (SMA, EMA, RSI, MACD, BB)
  portfolio.py                  # Portfolio tracker with JSON persistence
  chart.py                      # ASCII charting
```
