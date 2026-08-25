"""Normalized ATR â€” ATR as a percentage of close price."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.true_range import true_range
from quantindicators.library.wilder_ema import wilder_ema

_LOOKBACK = 3


class NormalizedATR(Indicator):
    """
    Normalized ATR.

    NormATR = ATR(period) / close * 100

    Expresses volatility as a percentage of price, making it comparable
    across symbols and different price levels over time.

    Returns float (> 0). Returns None when fewer than *period* + 1 bars
    are available or close is zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=14, ge=1)

    alias = "normalized_atr"

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
        atr = wilder_ema(tr, params.period)

        current_close = closes[-1]
        if current_close == 0.0:
            return None

        return float(atr / current_close * 100.0)

    def __repr__(self) -> str:
        return "NormalizedATR()"
