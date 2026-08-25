"""Momentum â€” absolute price change over N bars."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


class Momentum(Indicator):
    """
    Momentum: close - close[period] (absolute price change).

    Returns None when fewer than *period* + 1 bars are available.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=10, ge=1)

    alias = "momentum"

    async def compute(self, params: Parameters) -> float | None:
        rows = await self._store.fetch(self._symbol, self._interval, params.period + 1)
        if len(rows) < params.period + 1:
            return None
        return rows[-1]["close"] - rows[0]["close"]

    def __repr__(self) -> str:
        return "Momentum()"
