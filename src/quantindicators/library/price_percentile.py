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
        rows = await self._store.fetch(self._symbol, self._interval, params.period * _LOOKBACK)
        if len(rows) < params.period:
            return None

        closes = np.array([r["close"] for r in rows[-params.period :]], dtype=float)
        current = closes[-1]
        pct = float(np.sum(closes[:-1] < current) / (params.period - 1) * 100.0)
        return pct

    def __repr__(self) -> str:
        return "PricePercentile()"
