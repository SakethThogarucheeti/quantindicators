"""Distance from Moving Average â€” normalised rubber-band stretch."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class DistanceFromMA(Indicator):
    """
    Distance from Moving Average.

    (close - SMA(period)) / SMA(period) * 100

    Positive â†’ price stretched above MA (overbought).
    Negative â†’ price stretched below MA (oversold â†’ reversal up).

    Signal extractor: negate (negative = oversold stretch â†’ buy).

    Returns None when insufficient bars or SMA is zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=20, ge=2)

    alias = "distance_from_ma"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period * _LOOKBACK, "close", min_len=params.period)
        if cols is None:
            return None

        closes = cols["close"]
        sma = float(np.mean(closes[-params.period :]))
        if sma == 0:
            return None
        return float((closes[-1] - sma) / sma * 100.0)

    def __repr__(self) -> str:
        return "DistanceFromMA()"
