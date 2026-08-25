"""Candle Body Ratio â€” body size relative to total range."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class CandleBodyRatio(Indicator):
    """
    Candle Body Ratio.

    body  = |close - open|
    range = high - low
    ratio = body / range   â†’ [0, 1]

    High ratio â†’ conviction bar (strong move, low indecision).
    Low ratio  â†’ doji / indecision (potential reversal).

    Returns the smoothed ratio over *period* bars so single-bar noise
    is reduced. Returns None when insufficient bars or all ranges are zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=5, ge=1)

    alias = "candle_body_ratio"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            params.period * _LOOKBACK, "open", "high", "low", "close", min_len=params.period
        )
        if cols is None:
            return None

        opens = cols["open"][-params.period :]
        highs = cols["high"][-params.period :]
        lows = cols["low"][-params.period :]
        closes = cols["close"][-params.period :]

        ranges = highs - lows
        bodies = np.abs(closes - opens)
        valid = ranges > 0
        if not np.any(valid):
            return None
        return float(np.mean(bodies[valid] / ranges[valid]))

    def __repr__(self) -> str:
        return "CandleBodyRatio()"
