"""Interactive CLI for the stock analysis system."""

import sys
import textwrap

from stock_analysis.data import fetch_stock_data, get_stock_info, get_current_price, is_sample_mode
from stock_analysis.indicators import compute_all, generate_signals
from stock_analysis.chart import ascii_price_chart, ascii_rsi_chart
from stock_analysis.portfolio import Portfolio

BANNER = r"""
 ____  _             _        _                _           _
/ ___|| |_ ___   ___| | __   / \   _ __   __ _| |_   _ ___(_)___
\___ \| __/ _ \ / __| |/ /  / _ \ | '_ \ / _` | | | | / __| / __|
 ___) | || (_) | (__|   <  / ___ \| | | | (_| | | |_| \__ \ \__ \
|____/ \__\___/ \___|_|\_\/_/   \_\_| |_|\__,_|_|\__, |___/_|___/
                                                  |___/
"""

MENU = textwrap.dedent("""\
    ─────────────────────────────────────
      1) Stock Quote & Info
      2) Price Chart (ASCII)
      3) Technical Analysis & Signals
      4) Full Report (info + chart + signals)
      5) Portfolio — View
      6) Portfolio — Add Position
      7) Portfolio — Remove Position
      8) Compare Multiple Stocks
      0) Exit
    ─────────────────────────────────────
""")


def _header(title: str):
    width = 50
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val if val else default


# ── Menu handlers ────────────────────────────────────────────

def do_quote():
    symbol = _ask("Ticker symbol")
    if not symbol:
        return
    _header(f"Quote — {symbol.upper()}")
    try:
        info = get_stock_info(symbol)
        for key, val in info.items():
            label = key.replace("_", " ").title()
            if key == "marketCap" and isinstance(val, (int, float)):
                val = f"${val:,.0f}"
            elif key == "dividendYield" and isinstance(val, float):
                val = f"{val * 100:.2f}%"
            elif isinstance(val, float):
                val = f"{val:,.2f}"
            print(f"  {label:<25} {val}")
        price = get_current_price(symbol)
        print(f"  {'Latest Close':<25} ${price:,.2f}")
    except Exception as e:
        print(f"  Error: {e}")


def do_chart():
    symbol = _ask("Ticker symbol")
    period = _ask("Period (1mo/3mo/6mo/1y/2y/5y)", "6mo")
    if not symbol:
        return
    _header(f"Price Chart — {symbol.upper()} ({period})")
    try:
        df = fetch_stock_data(symbol, period=period)
        print(ascii_price_chart(df))
    except Exception as e:
        print(f"  Error: {e}")


def do_analysis():
    symbol = _ask("Ticker symbol")
    period = _ask("Period", "6mo")
    if not symbol:
        return
    _header(f"Technical Analysis — {symbol.upper()}")
    try:
        df = fetch_stock_data(symbol, period=period)
        df = compute_all(df)

        # Latest indicator values
        latest = df.iloc[-1]
        print(f"\n  Close:        ${latest['Close']:,.2f}")
        print(f"  SMA 20:       ${latest['SMA_20']:,.2f}")
        print(f"  SMA 50:       ${latest['SMA_50']:,.2f}")
        print(f"  EMA 12:       ${latest['EMA_12']:,.2f}")
        print(f"  EMA 26:       ${latest['EMA_26']:,.2f}")
        print(f"  RSI 14:       {latest['RSI_14']:.1f}")
        print(f"  MACD:         {latest['MACD']:.4f}")
        print(f"  MACD Signal:  {latest['MACD_Signal']:.4f}")
        print(f"  BB Upper:     ${latest['BB_Upper']:,.2f}")
        print(f"  BB Lower:     ${latest['BB_Lower']:,.2f}")

        # RSI chart
        print("\n  RSI Chart:")
        print(ascii_rsi_chart(df["RSI_14"]))

        # Signals
        _header("Signals")
        for sig in generate_signals(df):
            print(f"  -> {sig}")
    except Exception as e:
        print(f"  Error: {e}")


def do_full_report():
    symbol = _ask("Ticker symbol")
    period = _ask("Period", "6mo")
    if not symbol:
        return
    symbol = symbol.upper()

    # Info
    _header(f"Company Info — {symbol}")
    try:
        info = get_stock_info(symbol)
        for key, val in info.items():
            label = key.replace("_", " ").title()
            if key == "marketCap" and isinstance(val, (int, float)):
                val = f"${val:,.0f}"
            elif isinstance(val, float):
                val = f"{val:,.2f}"
            print(f"  {label:<25} {val}")
    except Exception as e:
        print(f"  Error fetching info: {e}")

    # Chart + analysis
    try:
        df = fetch_stock_data(symbol, period=period)
        _header(f"Price Chart — {symbol} ({period})")
        print(ascii_price_chart(df))

        df = compute_all(df)
        _header(f"Signals — {symbol}")
        for sig in generate_signals(df):
            print(f"  -> {sig}")
    except Exception as e:
        print(f"  Error: {e}")


def do_portfolio_view():
    _header("Portfolio")
    pf = Portfolio()
    rows = pf.summary()
    if not rows:
        print("  (empty — add positions with option 6)")
        return

    # Header row
    print(f"  {'Symbol':<8} {'Shares':>8} {'Avg Cost':>10} {'Price':>10} "
          f"{'Value':>12} {'P&L':>10} {'P&L %':>8}")
    print("  " + "-" * 78)
    for r in rows:
        price_str = f"${r['current_price']:,.2f}" if r["current_price"] else "N/A"
        mv_str = f"${r['market_value']:,.2f}" if r["market_value"] is not None else "N/A"
        pnl_str = f"${r['pnl']:,.2f}" if r["pnl"] is not None else "N/A"
        pct_str = f"{r['pnl_pct']:.1f}%" if r["pnl_pct"] is not None else "N/A"
        print(f"  {r['symbol']:<8} {r['shares']:>8.2f} ${r['avg_cost']:>9,.2f} "
              f"{price_str:>10} {mv_str:>12} {pnl_str:>10} {pct_str:>8}")

    total_cost, total_mv, total_pnl = pf.total_value()
    print("  " + "-" * 78)
    print(f"  {'TOTAL':<8} {'':>8} {'':>10} {'':>10} "
          f"${total_mv:>11,.2f} ${total_pnl:>9,.2f} "
          f"{(total_pnl / total_cost * 100) if total_cost else 0:.1f}%")


def do_portfolio_add():
    _header("Add Position")
    symbol = _ask("Ticker symbol")
    if not symbol:
        return
    try:
        shares = float(_ask("Number of shares"))
        cost = float(_ask("Cost per share ($)"))
    except ValueError:
        print("  Invalid number.")
        return
    pf = Portfolio()
    pf.add(symbol, shares, cost)
    print(f"  Added {shares} shares of {symbol.upper()} at ${cost:.2f}")


def do_portfolio_remove():
    _header("Remove Position")
    symbol = _ask("Ticker symbol to remove")
    if not symbol:
        return
    pf = Portfolio()
    if pf.remove(symbol):
        print(f"  Removed {symbol.upper()} from portfolio.")
    else:
        print(f"  {symbol.upper()} not found in portfolio.")


def do_compare():
    raw = _ask("Ticker symbols (comma-separated, e.g. AAPL,MSFT,GOOG)")
    if not raw:
        return
    symbols = [s.strip().upper() for s in raw.split(",") if s.strip()]
    period = _ask("Period", "6mo")

    _header("Stock Comparison")
    print(f"  {'Symbol':<8} {'Price':>10} {'Chg %':>8} {'RSI':>6} {'MACD':>10} {'Trend':>12}")
    print("  " + "-" * 60)

    for sym in symbols:
        try:
            df = fetch_stock_data(sym, period=period)
            df = compute_all(df)
            latest = df.iloc[-1]
            first_close = df["Close"].iloc[0]
            chg_pct = (latest["Close"] - first_close) / first_close * 100

            trend = "UP" if latest.get("SMA_20", 0) > latest.get("SMA_50", 0) else "DOWN"
            print(f"  {sym:<8} ${latest['Close']:>9,.2f} {chg_pct:>7.1f}% "
                  f"{latest['RSI_14']:>5.1f} {latest['MACD']:>10.4f} {trend:>12}")
        except Exception as e:
            print(f"  {sym:<8} Error: {e}")


# ── Main loop ────────────────────────────────────────────────

DISPATCH = {
    "1": do_quote,
    "2": do_chart,
    "3": do_analysis,
    "4": do_full_report,
    "5": do_portfolio_view,
    "6": do_portfolio_add,
    "7": do_portfolio_remove,
    "8": do_compare,
}


def main():
    print(BANNER)
    if is_sample_mode():
        print("  [SAMPLE DATA MODE] Yahoo Finance unavailable — using generated data.")
        print("  Prices are simulated. Connect to the internet for live quotes.\n")
    else:
        print("  [LIVE MODE] Connected to Yahoo Finance.\n")
    while True:
        print(MENU)
        choice = _ask("Choose an option", "0")
        if choice == "0":
            print("\n  Goodbye!\n")
            break
        handler = DISPATCH.get(choice)
        if handler:
            handler()
        else:
            print("  Invalid option. Try again.")


if __name__ == "__main__":
    main()
