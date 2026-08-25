"""Price vs 52-week High â€” how far price has fallen from its peak."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 1


class PriceVs52wHigh(Indicator):
    """
    Price vs N-bar High.

    (close - highest_high(period)) / highest_high(period) * 100

    Always <= 0. The more negative, the further price has fallen from peak.
    Deep negative = mean reversion anchor (price far from 52w high).

    Signal extractor: negate (more negative = more oversold = higher signal).

    Returns None when insufficient bars or high is zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=252, ge=2)

    alias = "price_vs_52w_high"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            params.period * _LOOKBACK, "high", "close", min_len=params.period
        )
        if cols is None:
            return None

        highs = cols["high"][-params.period :]
        closes = cols["close"]

        peak = float(np.max(highs))
        if peak == 0:
            return None
        return float((closes[-1] - peak) / peak * 100.0)

    def __repr__(self) -> str:
        return "PriceVs52wHigh()"
