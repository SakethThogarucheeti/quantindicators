"""Volatility Ratio â€” current ATR relative to its smoothed baseline."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.ema_series import ema_series as _ema_array
from quantindicators.library.true_range import true_range

_LOOKBACK = 3


class VolatilityRatio(Indicator):
    """
    Volatility Ratio.

    VR = ATR(atr_period) / EMA(ATR(atr_period), smooth_period)

    VR > 1 = volatility above baseline (potential mean-reversion regime).
    VR < 1 = compressed volatility (potential breakout setup).

    Returns ratio (float, > 0). Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        atr_period: int = Field(default=14, ge=1)
        smooth_period: int = Field(default=50, ge=2)

    alias = "volatility_ratio"

    async def compute(self, params: Parameters) -> float | None:
        limit = (params.atr_period + params.smooth_period) * _LOOKBACK
        cols = await self._fetch_columns(
            limit, "high", "low", "close", min_len=params.atr_period + params.smooth_period
        )
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]

        tr = true_range(highs, lows, closes)  # length == len(highs)

        # Build a rolling ATR array using Wilder EMA across the series
        atr_series = _ema_array(tr, params.atr_period)

        # Current ATR is the last value
        current_atr = atr_series[-1]

        # Smoothed ATR baseline (EMA of ATR array)
        smoothed = _ema_array(atr_series, params.smooth_period)
        baseline = smoothed[-1]

        if baseline == 0.0:
            return None

        return float(current_atr / baseline)

    def __repr__(self) -> str:
        return "VolatilityRatio()"
