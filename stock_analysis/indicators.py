"""Technical analysis indicators computed on pandas DataFrames."""

import pandas as pd


def sma(series: pd.Series, window: int = 20) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=window).mean()


def ema(series: pd.Series, span: int = 20) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index (0–100)."""
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD line, Signal line, and Histogram.

    Returns:
        Tuple of (macd_line, signal_line, histogram) as pd.Series.
    """
    ema_fast = ema(series, span=fast)
    ema_slow = ema(series, span=slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, span=signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0):
    """Bollinger Bands (upper, middle, lower).

    Returns:
        Tuple of (upper, middle, lower) as pd.Series.
    """
    middle = sma(series, window)
    std = series.rolling(window=window).std()
    upper = middle + num_std * std
    lower = middle - num_std * std
    return upper, middle, lower


def compute_all(df: pd.DataFrame) -> pd.DataFrame:
    """Attach all standard indicators to a price DataFrame.

    Expects a DataFrame with a 'Close' column. Returns a copy with new columns.
    """
    out = df.copy()
    close = out["Close"]

    out["SMA_20"] = sma(close, 20)
    out["SMA_50"] = sma(close, 50)
    out["EMA_12"] = ema(close, 12)
    out["EMA_26"] = ema(close, 26)
    out["RSI_14"] = rsi(close, 14)

    macd_line, signal_line, hist = macd(close)
    out["MACD"] = macd_line
    out["MACD_Signal"] = signal_line
    out["MACD_Hist"] = hist

    upper, middle, lower = bollinger_bands(close)
    out["BB_Upper"] = upper
    out["BB_Middle"] = middle
    out["BB_Lower"] = lower

    return out


def generate_signals(df: pd.DataFrame) -> list[str]:
    """Generate simple buy/sell/hold signals from the latest row of indicators.

    Args:
        df: DataFrame with indicator columns (from compute_all).

    Returns:
        List of human-readable signal strings.
    """
    if df.empty:
        return ["No data available."]

    latest = df.iloc[-1]
    signals = []

    # RSI signals
    rsi_val = latest.get("RSI_14")
    if pd.notna(rsi_val):
        if rsi_val < 30:
            signals.append(f"RSI ({rsi_val:.1f}) is OVERSOLD — potential BUY signal")
        elif rsi_val > 70:
            signals.append(f"RSI ({rsi_val:.1f}) is OVERBOUGHT — potential SELL signal")
        else:
            signals.append(f"RSI ({rsi_val:.1f}) is neutral")

    # MACD crossover
    macd_val = latest.get("MACD")
    signal_val = latest.get("MACD_Signal")
    if pd.notna(macd_val) and pd.notna(signal_val):
        if macd_val > signal_val:
            signals.append("MACD is ABOVE signal line — bullish momentum")
        else:
            signals.append("MACD is BELOW signal line — bearish momentum")

    # Bollinger Band position
    close = latest.get("Close")
    bb_upper = latest.get("BB_Upper")
    bb_lower = latest.get("BB_Lower")
    if pd.notna(close) and pd.notna(bb_upper) and pd.notna(bb_lower):
        if close >= bb_upper:
            signals.append("Price at UPPER Bollinger Band — may be overextended")
        elif close <= bb_lower:
            signals.append("Price at LOWER Bollinger Band — may be undervalued")
        else:
            signals.append("Price within Bollinger Bands — normal range")

    # SMA trend
    sma20 = latest.get("SMA_20")
    sma50 = latest.get("SMA_50")
    if pd.notna(sma20) and pd.notna(sma50):
        if sma20 > sma50:
            signals.append("SMA 20 > SMA 50 — short-term UPTREND")
        else:
            signals.append("SMA 20 < SMA 50 — short-term DOWNTREND")

    return signals if signals else ["Insufficient data for signal generation."]
