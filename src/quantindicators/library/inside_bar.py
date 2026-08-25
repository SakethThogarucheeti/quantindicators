"""Inside Bar â€” coiling / compression before a swing move."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class InsideBar(Indicator):
    """
    Inside Bar ratio.

    An inside bar is one where high < prev_high and low > prev_low â€”
    the bar is completely contained within the previous bar's range.

    Returns the fraction of the last *period* bars that are inside bars,
    as a value in [0, 1]. High reading = compression / coiling.

    Not directly a directional signal â€” combine with RSI direction.
    As-is: high value = compressed volatility (often precedes breakout).

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=10, ge=2)

    alias = "inside_bar"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            (params.period + 1) * _LOOKBACK, "high", "low", min_len=params.period + 1
        )
        if cols is None:
            return None

        highs = cols["high"][-(params.period + 1) :]
        lows = cols["low"][-(params.period + 1) :]

        count = 0
        for i in range(1, params.period + 1):
            if highs[i] < highs[i - 1] and lows[i] > lows[i - 1]:
                count += 1
        return float(count / params.period)

    def __repr__(self) -> str:
        return "InsideBar()"
