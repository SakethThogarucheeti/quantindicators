"""Volume Rate of Change â€” percentage change in volume over N bars."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


class VROC(Indicator):
    """
    Volume Rate of Change.

    VROC = (volume_now - volume_N_bars_ago) / volume_N_bars_ago * 100

    Returns percentage; positive = volume expanding, negative = contracting.
    Returns None when fewer than *period* + 1 bars are available or when
    the reference bar volume is zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=14, ge=1)

    alias = "vroc"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period + 1, "volume")
        if cols is None:
            return None

        volumes = cols["volume"]
        ref = volumes[0]
        if ref == 0.0:
            return None

        return float((volumes[-1] - ref) / ref * 100.0)

    def __repr__(self) -> str:
        return "VROC()"
