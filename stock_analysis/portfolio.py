"""Portfolio tracker — persist holdings in a JSON file and compute P&L."""

import json
import os
from pathlib import Path

from stock_analysis.data import get_current_price

DEFAULT_PATH = Path.home() / ".stock_portfolio.json"


class Portfolio:
    """Simple portfolio: tracks symbol, shares, and average cost."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DEFAULT_PATH
        self.holdings: dict[str, dict] = {}  # symbol -> {shares, avg_cost}
        self._load()

    # ── persistence ──────────────────────────────────────────────

    def _load(self):
        if self.path.exists():
            with open(self.path) as f:
                self.holdings = json.load(f)

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.holdings, f, indent=2)

    # ── mutations ────────────────────────────────────────────────

    def add(self, symbol: str, shares: float, cost_per_share: float):
        """Add a position (or average into an existing one)."""
        symbol = symbol.upper()
        if symbol in self.holdings:
            existing = self.holdings[symbol]
            total_shares = existing["shares"] + shares
            total_cost = (existing["shares"] * existing["avg_cost"]) + (shares * cost_per_share)
            existing["shares"] = total_shares
            existing["avg_cost"] = total_cost / total_shares
        else:
            self.holdings[symbol] = {"shares": shares, "avg_cost": cost_per_share}
        self._save()

    def remove(self, symbol: str):
        """Remove an entire position."""
        symbol = symbol.upper()
        if symbol in self.holdings:
            del self.holdings[symbol]
            self._save()
            return True
        return False

    # ── queries ──────────────────────────────────────────────────

    def summary(self) -> list[dict]:
        """Return a list of position dicts with live P&L."""
        rows = []
        for symbol, pos in sorted(self.holdings.items()):
            try:
                price = get_current_price(symbol)
            except Exception:
                price = None

            shares = pos["shares"]
            avg_cost = pos["avg_cost"]
            cost_basis = shares * avg_cost
            market_value = shares * price if price else None
            pnl = market_value - cost_basis if market_value is not None else None
            pnl_pct = (pnl / cost_basis * 100) if pnl is not None and cost_basis else None

            rows.append({
                "symbol": symbol,
                "shares": shares,
                "avg_cost": avg_cost,
                "current_price": price,
                "cost_basis": cost_basis,
                "market_value": market_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
            })
        return rows

    def total_value(self) -> tuple[float, float, float]:
        """Return (total_cost, total_market_value, total_pnl)."""
        rows = self.summary()
        total_cost = sum(r["cost_basis"] for r in rows)
        total_mv = sum(r["market_value"] for r in rows if r["market_value"] is not None)
        total_pnl = total_mv - total_cost
        return total_cost, total_mv, total_pnl
