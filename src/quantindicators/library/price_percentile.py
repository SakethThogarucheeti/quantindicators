"""Price Percentile â€” where current close sits within its N-bar distribution."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class PricePercentile(Indicator):
    """
    Price Percentile.

    Fraction of the last *period* closes that are below the current close,
    expressed as [0, 100].

    0  â†’ current close is the lowest in the window (oversold)
    100 â†’ current close is the highest (overbought)

    More robust than Bollinger %B â€” makes no Gaussian assumption.
    Signal extractor: negate (low percentile = oversold â†’ reversal up).

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=50, ge=2)

    alias = "price_percentile"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period * _LOOKBACK, "close", min_len=params.period)
        if cols is None:
            return None

        closes = cols["close"][-params.period :]
        current = closes[-1]
        pct = float(np.sum(closes[:-1] < current) / (params.period - 1) * 100.0)
        return pct

    def __repr__(self) -> str:
        return "PricePercentile()"
