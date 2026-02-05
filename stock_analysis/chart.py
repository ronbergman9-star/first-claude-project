"""ASCII charting for terminal display."""

import pandas as pd


def _scale(values: list[float], height: int) -> list[int]:
    """Map float values to integer row indices 0..height-1."""
    mn, mx = min(values), max(values)
    spread = mx - mn if mx != mn else 1.0
    return [int((v - mn) / spread * (height - 1)) for v in values]


def ascii_price_chart(df: pd.DataFrame, width: int = 80, height: int = 20) -> str:
    """Render a simple ASCII closing-price chart.

    Downsamples to *width* data points and scales vertically to *height* rows.
    """
    close = df["Close"].dropna().tolist()
    if len(close) == 0:
        return "(no data)"

    # Downsample to fit width
    if len(close) > width:
        step = len(close) / width
        close = [close[int(i * step)] for i in range(width)]

    mn, mx = min(close), max(close)
    scaled = _scale(close, height)

    # Build grid (row 0 = bottom)
    grid = [[" "] * len(scaled) for _ in range(height)]
    for col, row in enumerate(scaled):
        grid[row][col] = "\u2588"  # full-block character

    lines = []
    for row_idx in range(height - 1, -1, -1):
        price = mn + (mx - mn) * row_idx / (height - 1) if height > 1 else mn
        label = f"{price:>10.2f} |"
        lines.append(label + "".join(grid[row_idx]))

    # X-axis
    lines.append(" " * 11 + "+" + "-" * len(scaled))

    # Date labels (start, middle, end)
    dates = df.index
    if len(dates) >= 2:
        start = dates[0].strftime("%Y-%m-%d")
        end = dates[-1].strftime("%Y-%m-%d")
        spacer = len(scaled) - len(start) - len(end)
        if spacer < 1:
            spacer = 1
        lines.append(" " * 11 + " " + start + " " * spacer + end)

    return "\n".join(lines)


def ascii_rsi_chart(rsi_series: pd.Series, width: int = 80, height: int = 10) -> str:
    """Render RSI as an ASCII chart with 30/70 reference lines."""
    values = rsi_series.dropna().tolist()
    if not values:
        return "(no RSI data)"

    if len(values) > width:
        step = len(values) / width
        values = [values[int(i * step)] for i in range(width)]

    # Fixed 0-100 scale
    grid = [[" "] * len(values) for _ in range(height)]

    for col, val in enumerate(values):
        row = int(val / 100 * (height - 1))
        row = max(0, min(height - 1, row))
        grid[row][col] = "\u2588"

    # Reference rows for 30 and 70
    row_30 = int(30 / 100 * (height - 1))
    row_70 = int(70 / 100 * (height - 1))

    lines = []
    for row_idx in range(height - 1, -1, -1):
        level = int(100 * row_idx / (height - 1)) if height > 1 else 0
        label = f"{level:>6} |"
        row_chars = list(grid[row_idx])
        # Draw reference lines where empty
        if row_idx in (row_30, row_70):
            for c in range(len(row_chars)):
                if row_chars[c] == " ":
                    row_chars[c] = "\u00b7"  # middle dot
        lines.append(label + "".join(row_chars))

    lines.append(" " * 7 + "+" + "-" * len(values))
    return "\n".join(lines)
