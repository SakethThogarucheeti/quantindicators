"""Ultimate Oscillator â€” multi-timeframe buying pressure."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.true_range import true_range


class UltimateOscillator(Indicator):
    """
    Ultimate Oscillator (Larry Williams, 1976).

    Buying Pressure  = close - min(low, prev_close)
    True Range       = max(high, prev_close) - min(low, prev_close)
    UO = 100 * (4*avg(BP/TR, p1) + 2*avg(BP/TR, p2) + avg(BP/TR, p3)) / 7

    Returns [0, 100]. Oversold < 30, overbought > 70.
    """

    class Parameters(IndicatorParameters):
        period1: int = Field(default=7, ge=1)
        period2: int = Field(default=14, ge=1)
        period3: int = Field(default=28, ge=1)

    alias = "ultimate_oscillator"

    async def compute(self, params: Parameters) -> float | None:
        if not (params.period1 < params.period2 < params.period3):
            return None
        cols = await self._fetch_columns(params.period3 + 1, "high", "low", "close")
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]

        tr = true_range(highs, lows, closes)  # length == len(highs)

        # Buying pressure: close - min(low, prev_close), bars 1..n
        prev_closes = closes[:-1]
        bp = closes[1:] - np.minimum(lows[1:], prev_closes)
        tr_vals = tr[1:]  # align with bp

        def _avg(arr_bp: np.ndarray, arr_tr: np.ndarray, period: int) -> float:
            bp_sum = float(np.sum(arr_bp[-period:]))
            tr_sum = float(np.sum(arr_tr[-period:]))
            return bp_sum / tr_sum if tr_sum > 0.0 else 0.5

        avg1 = _avg(bp, tr_vals, params.period1)
        avg2 = _avg(bp, tr_vals, params.period2)
        avg3 = _avg(bp, tr_vals, params.period3)

        return 100.0 * (4.0 * avg1 + 2.0 * avg2 + avg3) / 7.0

    def __repr__(self) -> str:
        return "UltimateOscillator()"
