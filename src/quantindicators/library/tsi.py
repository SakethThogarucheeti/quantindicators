"""True Strength Index â€” double-smoothed momentum oscillator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.ema_series import ema_series as _ema

if TYPE_CHECKING:
    pass

_LOOKBACK = 3


class TSI(Indicator):
    """
    True Strength Index.

    TSI = 100 * EMA(EMA(price_change, fast), slow)
              / EMA(EMA(|price_change|, fast), slow)

    Returns [-100, 100]. Positive = bullish momentum, negative = bearish.
    Overbought > 25, oversold < -25.
    Returns None when fewer than (fast + slow) * LOOKBACK bars available.
    """

    class Parameters(IndicatorParameters):
        fast: int = Field(default=13, ge=1)
        slow: int = Field(default=25, ge=1)

    alias = "tsi"

    async def compute(self, params: Parameters) -> float | None:
        if params.slow <= params.fast:
            return None
        limit = (params.fast + params.slow) * _LOOKBACK
        rows = await self._store.fetch(self._symbol, self._interval, limit)
        if len(rows) < params.fast + params.slow + 1:
            return None

        closes = np.array([r["close"] for r in rows], dtype=float)
        pc = np.diff(closes)  # 1-bar price change
        apc = np.abs(pc)  # absolute price change

        # Double smooth
        smooth_pc = _ema(_ema(pc, params.fast), params.slow)
        smooth_apc = _ema(_ema(apc, params.fast), params.slow)

        denom = smooth_apc[-1]
        if denom == 0.0:
            return None

        return 100.0 * smooth_pc[-1] / denom

    def __repr__(self) -> str:
        return "TSI()"
