"""Session High-Low Pct — position within today's intraday range."""

from __future__ import annotations

from datetime import datetime

import numpy as np

from quantindicators.base import Indicator, IndicatorParameters


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

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns_since(
            params.session_open_utc, "high", "low", "close"
        )
        if cols is None:
            return None

        session_high = float(np.max(cols["high"]))
        session_low = float(np.min(cols["low"]))
        rng = session_high - session_low

        if rng == 0.0:
            return None

        current_close = float(cols["close"][-1])
        return (current_close - session_low) / rng

    def __repr__(self) -> str:
        return "SessionHighLowPct()"
