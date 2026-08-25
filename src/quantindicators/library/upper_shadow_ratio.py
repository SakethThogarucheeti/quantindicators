"""Upper Shadow Ratio â€” rejection of highs, bearish wick signal."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class UpperShadowRatio(Indicator):
    """
    Upper Shadow Ratio.

    upper_shadow = high - max(open, close)
    ratio        = upper_shadow / (high - low)   â†’ [0, 1]

    High ratio â†’ strong rejection at the top (bearish wick).
    Smoothed over *period* bars. High reading = overhead resistance = reversal down.

    Signal extractor: negate (high upper shadow â†’ overbought rejection â†’ sell).

    Returns None when insufficient bars or all ranges are zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=5, ge=1)

    alias = "upper_shadow_ratio"

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
        upper_shadows = highs - np.maximum(opens, closes)
        valid = ranges > 0
        if not np.any(valid):
            return None
        return float(np.mean(upper_shadows[valid] / ranges[valid]))

    def __repr__(self) -> str:
        return "UpperShadowRatio()"
