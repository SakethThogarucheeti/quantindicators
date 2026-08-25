"""Chandelier Exit â€” ATR-based measure of how extended price is from recent high."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.true_range import true_range
from quantindicators.library.wilder_ema import wilder_ema

_LOOKBACK = 3


class ChandelierExit(Indicator):
    """
    Chandelier Exit distance.

    chandelier_long  = highest_high(period) - ATR(period) * multiplier
    distance         = (close - chandelier_long) / close * 100

    Positive â†’ price well above the exit line (not stretched down).
    Negative â†’ price has fallen below the chandelier (oversold, stretched).

    Signal extractor: negate (negative = price below chandelier = buy setup).

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=22, ge=2)
        multiplier: float = Field(default=3.0, gt=0)

    alias = "chandelier_exit"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            params.period * _LOOKBACK, "high", "low", "close", min_len=params.period + 1
        )
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]

        tr = true_range(highs, lows, closes)
        atr = wilder_ema(tr[-params.period :], params.period)
        highest_high = float(np.max(highs[-params.period :]))
        chandelier = highest_high - atr * params.multiplier

        current_close = closes[-1]
        if current_close == 0:
            return None
        return float((current_close - chandelier) / current_close * 100.0)

    def __repr__(self) -> str:
        return "ChandelierExit()"
