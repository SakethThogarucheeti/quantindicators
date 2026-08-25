"""Detrended Price Oscillator â€” removes dominant trend to expose cycles."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


class DPO(Indicator):
    """
    Detrended Price Oscillator.

    DPO = close - SMA(close, period) shifted back (period // 2 + 1) bars.

    The shift removes the trend component, leaving oscillations around
    the mid-cycle average. Positive = above detrended mean (overbought),
    Negative = below (oversold).

    Returns None when fewer than *period* + shift bars are available.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=20, ge=2)

    alias = "dpo"

    async def compute(self, params: Parameters) -> float | None:
        shift = params.period // 2 + 1
        limit = params.period + shift
        cols = await self._fetch_columns(limit, "close")
        if cols is None:
            return None

        closes = cols["close"]

        # SMA of the window ending at bar (limit - shift - 1)
        sma_window = closes[: params.period]
        sma = float(np.mean(sma_window))

        # Current close is the last bar
        current_close = closes[-1]
        return current_close - sma

    def __repr__(self) -> str:
        return "DPO()"
