from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .watchlist import WatchTarget


def load_trade_baselines(data_dir: Path, targets: tuple[WatchTarget, ...]) -> dict[str, int]:
    baselines: dict[str, int] = {}
    for target in targets:
        path = data_dir / "trades" / f"{target.complex_id}.json"
        if not path.exists():
            continue

        payload = json.loads(path.read_text(encoding="utf-8"))
        raw_trades = payload.get("trades", payload) if isinstance(payload, dict) else payload
        if not isinstance(raw_trades, list):
            continue

        prices = [_price_krw(trade) for trade in raw_trades if isinstance(trade, dict)]
        prices = [price for price in prices if price > 0]
        if prices:
            baselines[target.complex_id] = int(sum(prices) / len(prices))
    return baselines


def _price_krw(trade: dict[str, Any]) -> int:
    try:
        value = trade.get("price_krw", trade.get("trade_price_krw"))
        if isinstance(value, bool):
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0
