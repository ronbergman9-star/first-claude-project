#!/usr/bin/env python3
"""Stock price tracker that fetches the latest price and gives a simple daily analysis."""

import sys
import requests


def fetch_stock_data(symbol):
    """Fetch current and previous close price from Yahoo Finance."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {"range": "2d", "interval": "1d"}
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    result = data.get("chart", {}).get("result")
    if not result:
        return None

    meta = result[0].get("meta", {})
    closes = result[0].get("indicators", {}).get("quote", [{}])[0].get("close", [])

    if len(closes) >= 2 and closes[-2] is not None and closes[-1] is not None:
        return {"prev_close": closes[-2], "latest_close": closes[-1]}

    # Fallback: use meta fields
    prev = meta.get("chartPreviousClose") or meta.get("previousClose")
    curr = meta.get("regularMarketPrice")
    if prev is not None and curr is not None:
        return {"prev_close": prev, "latest_close": curr}

    return None


def main():
    symbol = input("Enter a stock symbol (e.g. AAPL): ").strip().upper()
    if not symbol:
        print("No symbol entered.")
        sys.exit(1)

    try:
        data = fetch_stock_data(symbol)
    except requests.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)

    if data is None:
        print(f"Could not fetch data for '{symbol}'. Check the symbol and try again.")
        sys.exit(1)

    prev_close = data["prev_close"]
    latest_close = data["latest_close"]
    change = latest_close - prev_close
    pct_change = (change / prev_close) * 100

    print(f"\n{symbol}")
    print(f"  Previous close: ${prev_close:.2f}")
    print(f"  Latest price:   ${latest_close:.2f}")
    print(f"  Change:         {change:+.2f} ({pct_change:+.2f}%)")

    if latest_close >= prev_close:
        print(f"\n  Price went up today.")
    else:
        print(f"\n  Price went down today.")


if __name__ == "__main__":
    main()
