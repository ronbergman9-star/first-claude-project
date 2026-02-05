"""Generate realistic sample stock data for offline / demo use."""

import math
import random
from datetime import datetime, timedelta

import pandas as pd

# Seed profiles: base price, volatility, drift, sector info
PROFILES = {
    "AAPL": {"base": 185.0, "vol": 0.018, "drift": 0.0003, "name": "Apple Inc.",
             "sector": "Technology", "industry": "Consumer Electronics",
             "marketCap": 2_900_000_000_000, "pe": 29.5, "divYield": 0.0052},
    "MSFT": {"base": 410.0, "vol": 0.016, "drift": 0.0004, "name": "Microsoft Corp.",
             "sector": "Technology", "industry": "Software",
             "marketCap": 3_100_000_000_000, "pe": 35.2, "divYield": 0.0073},
    "GOOG": {"base": 155.0, "vol": 0.020, "drift": 0.0002, "name": "Alphabet Inc.",
             "sector": "Technology", "industry": "Internet Services",
             "marketCap": 1_950_000_000_000, "pe": 25.1, "divYield": 0.0},
    "AMZN": {"base": 185.0, "vol": 0.022, "drift": 0.0003, "name": "Amazon.com Inc.",
             "sector": "Consumer Cyclical", "industry": "E-Commerce",
             "marketCap": 1_900_000_000_000, "pe": 60.8, "divYield": 0.0},
    "TSLA": {"base": 245.0, "vol": 0.035, "drift": 0.0001, "name": "Tesla Inc.",
             "sector": "Consumer Cyclical", "industry": "Auto Manufacturers",
             "marketCap": 780_000_000_000, "pe": 65.3, "divYield": 0.0},
    "NVDA": {"base": 480.0, "vol": 0.028, "drift": 0.0006, "name": "NVIDIA Corp.",
             "sector": "Technology", "industry": "Semiconductors",
             "marketCap": 1_200_000_000_000, "pe": 62.0, "divYield": 0.0004},
    "JPM":  {"base": 195.0, "vol": 0.014, "drift": 0.0002, "name": "JPMorgan Chase & Co.",
             "sector": "Financial Services", "industry": "Banks",
             "marketCap": 560_000_000_000, "pe": 11.8, "divYield": 0.0240},
    "JNJ":  {"base": 158.0, "vol": 0.010, "drift": 0.0001, "name": "Johnson & Johnson",
             "sector": "Healthcare", "industry": "Pharmaceuticals",
             "marketCap": 380_000_000_000, "pe": 15.6, "divYield": 0.0300},
    "V":    {"base": 275.0, "vol": 0.013, "drift": 0.0003, "name": "Visa Inc.",
             "sector": "Financial Services", "industry": "Credit Services",
             "marketCap": 560_000_000_000, "pe": 30.0, "divYield": 0.0076},
    "WMT":  {"base": 165.0, "vol": 0.011, "drift": 0.0002, "name": "Walmart Inc.",
             "sector": "Consumer Defensive", "industry": "Discount Stores",
             "marketCap": 440_000_000_000, "pe": 27.3, "divYield": 0.0140},
}

PERIOD_DAYS = {
    "1mo": 22, "3mo": 66, "6mo": 132, "1y": 252, "2y": 504, "5y": 1260,
    "5d": 5, "1d": 1, "max": 2520,
}


def _generate_prices(base: float, vol: float, drift: float, n_days: int,
                      seed: int | None = None) -> list[dict]:
    """Geometric Brownian Motion-ish daily OHLCV data."""
    rng = random.Random(seed)
    price = base * (1 + rng.gauss(0, 0.05))  # slight random start offset
    rows = []
    for i in range(n_days):
        daily_return = drift + vol * rng.gauss(0, 1)
        # Add slight mean-reversion to keep prices realistic
        daily_return -= 0.001 * (price / base - 1)
        close = price * (1 + daily_return)
        high = close * (1 + abs(rng.gauss(0, vol * 0.5)))
        low = close * (1 - abs(rng.gauss(0, vol * 0.5)))
        opn = price * (1 + rng.gauss(0, vol * 0.3))
        volume = int(rng.gauss(50_000_000, 15_000_000))
        volume = max(volume, 1_000_000)
        rows.append({"Open": opn, "High": max(high, opn), "Low": min(low, opn),
                      "Close": close, "Volume": volume})
        price = close
    return rows


def generate_stock_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """Generate sample OHLCV data for a given symbol and period.

    If the symbol is unknown, generates data with a random profile.
    """
    symbol = symbol.upper()
    n_days = PERIOD_DAYS.get(period, 132)

    if symbol in PROFILES:
        p = PROFILES[symbol]
        base, vol, drift = p["base"], p["vol"], p["drift"]
    else:
        # Unknown ticker: generate random but stable profile from symbol hash
        h = hash(symbol) % 10000
        base = 20 + (h % 500)
        vol = 0.012 + (h % 30) * 0.001
        drift = -0.0002 + (h % 10) * 0.0001

    seed = hash(symbol + period) & 0xFFFFFFFF
    rows = _generate_prices(base, vol, drift, n_days, seed=seed)

    end_date = datetime(2026, 2, 5)
    dates = pd.bdate_range(end=end_date, periods=n_days)
    df = pd.DataFrame(rows, index=dates)
    df.index.name = "Date"
    return df


def generate_stock_info(symbol: str) -> dict:
    """Return sample company info for a symbol."""
    symbol = symbol.upper()
    if symbol in PROFILES:
        p = PROFILES[symbol]
        return {
            "shortName": p["name"],
            "sector": p["sector"],
            "industry": p["industry"],
            "marketCap": p["marketCap"],
            "trailingPE": p["pe"],
            "forwardPE": round(p["pe"] * 0.92, 1),
            "dividendYield": p["divYield"],
            "fiftyTwoWeekHigh": round(p["base"] * 1.25, 2),
            "fiftyTwoWeekLow": round(p["base"] * 0.78, 2),
            "averageVolume": 52_000_000,
            "currency": "USD",
            "exchange": "NMS",
        }
    # Generic fallback
    return {
        "shortName": f"{symbol} Corp. (sample)",
        "sector": "N/A",
        "industry": "N/A",
        "marketCap": "N/A",
        "trailingPE": "N/A",
        "forwardPE": "N/A",
        "dividendYield": "N/A",
        "fiftyTwoWeekHigh": "N/A",
        "fiftyTwoWeekLow": "N/A",
        "averageVolume": "N/A",
        "currency": "USD",
        "exchange": "N/A",
    }
