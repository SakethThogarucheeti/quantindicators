"""Elder Ray â€” Bull/Bear Power relative to EMA."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 3


def _ema(values: np.ndarray, period: int) -> float:
    alpha = 2.0 / (period + 1)
    acc = values[0]
    for v in values[1:]:
        acc = alpha * v + (1.0 - alpha) * acc
    return acc


class ElderRay(Indicator):
    """
    Elder Ray Index â€” Bull Power and Bear Power combined.

    bull_power = high - EMA(close, period)
    bear_power = low  - EMA(close, period)
    elder_ray  = bull_power + bear_power  (net power)

    Positive â†’ price action above EMA (bullish context).
    Negative â†’ price action below EMA (bearish context, mean reversion up).

    Signal extractor: negate (negative elder_ray = oversold stretch â†’ reversal).

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=13, ge=2)

    alias = "elder_ray"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            params.period * _LOOKBACK, "high", "low", "close", min_len=params.period
        )
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]

        ema = _ema(closes, params.period)
        bull_power = highs[-1] - ema
        bear_power = lows[-1] - ema
        return float(bull_power + bear_power)

    def __repr__(self) -> str:
        return "ElderRay()"
