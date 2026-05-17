"""Session High-Low Pct — position within today's intraday range."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np

from quantindicators.base import Indicator, IndicatorParameters

if TYPE_CHECKING:
    from quantindicators.store import AbstractCandleStore


class SessionHighLowPct(Indicator):
    """
    Position of the current close within today's session range so far.

        (close - session_low) / (session_high - session_low)

    Returns [0, 1]: 0 = at session low, 1 = at session high.
    Returns None if fewer than 2 session bars are available or range == 0.
    The caller is responsible for computing session_open_utc.
    """

    class Parameters(IndicatorParameters):
        session_open_utc: datetime

    alias = "session_hl_pct"

    async def compute(self, params: Parameters) -> float | None:  # type: ignore[override]
        rows = await self._store.fetch_since(self._symbol, self._interval, params.session_open_utc)
        if len(rows) < 2:
            return None

        highs = np.array([r["high"] for r in rows], dtype=float)
        lows = np.array([r["low"] for r in rows], dtype=float)

        session_high = float(np.max(highs))
        session_low = float(np.min(lows))
        rng = session_high - session_low

        if rng == 0.0:
            return None

        current_close = float(rows[-1]["close"])
        return (current_close - session_low) / rng

    def __repr__(self) -> str:
        return "SessionHighLowPct()"
