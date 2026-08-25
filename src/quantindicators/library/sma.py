"""Simple Moving Average."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


class SMA(Indicator):
    """
    Arithmetic mean of the last *period* closing prices.

    Returns None when fewer than *period* bars are available.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=20, ge=1)

    alias = "sma"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period, "close")
        if cols is None:
            return None
        closes = cols["close"]
        return float(np.mean(closes))

    def __repr__(self) -> str:
        return "SMA()"
