"""Stochastic RSI â€” RSI normalised within its own N-bar range."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.rsi_series import rsi_series as _rsi_series

_LOOKBACK = 3


class StochasticRSI(Indicator):
    """
    Stochastic RSI.

    StochRSI = (RSI - min(RSI, period)) / (max(RSI, period) - min(RSI, period))

    Ranges [0, 100]. More sensitive than plain RSI â€” useful for picking
    intraday and swing exhaustion points earlier.

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        rsi_period: int = Field(default=14, ge=2)
        stoch_period: int = Field(default=14, ge=2)

    alias = "stochastic_rsi"

    async def compute(self, params: Parameters) -> float | None:
        needed = (params.rsi_period + params.stoch_period) * _LOOKBACK
        cols = await self._fetch_columns(
            needed, "close", min_len=params.rsi_period + params.stoch_period + 1
        )
        if cols is None:
            return None

        closes = cols["close"]
        rsi = _rsi_series(closes, params.rsi_period)
        valid = rsi[~np.isnan(rsi)]
        if len(valid) < params.stoch_period:
            return None

        window = valid[-params.stoch_period :]
        lo, hi = float(np.min(window)), float(np.max(window))
        if hi == lo:
            return None
        return float((valid[-1] - lo) / (hi - lo) * 100.0)

    def __repr__(self) -> str:
        return "StochasticRSI()"
