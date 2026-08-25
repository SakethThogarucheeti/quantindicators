"""Volume-Weighted Moving Average."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


class VWMA(Indicator):
    """
    Volume-Weighted Moving Average.

    VWMA = sum(close * volume, period) / sum(volume, period)

    Like SMA but bars with higher volume carry more weight.
    Returns None when fewer than *period* bars or total volume is zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=20, ge=1)

    alias = "vwma"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period, "close", "volume")
        if cols is None:
            return None
        closes = cols["close"]
        volumes = cols["volume"]

        total_vol = volumes.sum()
        if total_vol == 0.0:
            return None
        return float((closes * volumes).sum() / total_vol)

    def __repr__(self) -> str:
        return "VWMA()"
