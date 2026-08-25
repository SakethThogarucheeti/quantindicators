"""Upper Shadow Ratio â€” rejection of highs, bearish wick signal."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


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
        return await self._ohlc_ratio(
            params.period, lambda opens, highs, lows, closes: highs - np.maximum(opens, closes)
        )

    def __repr__(self) -> str:
        return "UpperShadowRatio()"
