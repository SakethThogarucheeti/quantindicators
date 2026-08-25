"""Volume-Weighted Moving Average."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.vwap import volume_weighted_average


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
        return volume_weighted_average(cols["close"], cols["volume"])

    def __repr__(self) -> str:
        return "VWMA()"
