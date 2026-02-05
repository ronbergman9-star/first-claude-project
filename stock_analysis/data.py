"""Stock data fetching module.

Uses Yahoo Finance (yfinance) when network access is available.
Falls back to built-in sample data for offline / sandboxed environments.
"""

import pandas as pd

from stock_analysis.sample_data import generate_stock_data, generate_stock_info

# Try to import yfinance — not strictly required at runtime
try:
    import yfinance as yf
    _HAS_YF = True
except ImportError:
    _HAS_YF = False

_USE_SAMPLE: bool | None = None  # auto-detect on first call


def _detect_mode() -> bool:
    """Return True if we should use sample data (offline)."""
    global _USE_SAMPLE
    if _USE_SAMPLE is not None:
        return _USE_SAMPLE

    if not _HAS_YF:
        _USE_SAMPLE = True
        return True

    # Probe with a quick call
    try:
        t = yf.Ticker("AAPL")
        info = t.info
        if info and info.get("regularMarketPrice"):
            _USE_SAMPLE = False
            return False
    except Exception:
        pass

    _USE_SAMPLE = True
    return True


def fetch_stock_data(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical stock data.

    Args:
        symbol: Ticker symbol (e.g. "AAPL", "MSFT").
        period: Data period — 1d,5d,1mo,3mo,6mo,1y,2y,5y,max.
        interval: Data interval (used only in live mode).

    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume.
    """
    if _detect_mode():
        return generate_stock_data(symbol, period=period)

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    if df.empty:
        raise ValueError(f"No data found for symbol '{symbol}'. Check the ticker.")
    df.index = df.index.tz_localize(None) if df.index.tz else df.index
    return df[["Open", "High", "Low", "Close", "Volume"]]


def get_stock_info(symbol: str) -> dict:
    """Get basic company info for a ticker."""
    if _detect_mode():
        return generate_stock_info(symbol)

    ticker = yf.Ticker(symbol)
    info = ticker.info
    keys = [
        "shortName", "sector", "industry", "marketCap",
        "trailingPE", "forwardPE", "dividendYield",
        "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "averageVolume",
        "currency", "exchange",
    ]
    return {k: info.get(k, "N/A") for k in keys}


def get_current_price(symbol: str) -> float:
    """Return the most recent closing price for a symbol."""
    df = fetch_stock_data(symbol, period="5d", interval="1d")
    return float(df["Close"].iloc[-1])


def is_sample_mode() -> bool:
    """Return True if the system is using generated sample data."""
    return _detect_mode()
