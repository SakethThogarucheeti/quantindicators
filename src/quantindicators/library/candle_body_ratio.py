"""Candle Body Ratio â€” body size relative to total range."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


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
        return await self._ohlc_ratio(
            params.period, lambda opens, highs, lows, closes: np.abs(closes - opens)
        )

    def __repr__(self) -> str:
        return "CandleBodyRatio()"
