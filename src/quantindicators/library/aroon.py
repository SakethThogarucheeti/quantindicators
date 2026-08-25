"""Aroon Oscillator â€” measures recency of highs vs lows."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class Aroon(Indicator):
    """
    Aroon Oscillator.

    aroon_up   = (period - bars_since_high) / period * 100
    aroon_down = (period - bars_since_low)  / period * 100
    oscillator = aroon_up - aroon_down

    Range [-100, 100].
    Negative (recent lows) â†’ oversold swing setup â†’ mean reversion up.

    Signal extractor: negate (negative oscillator = potential reversal up).

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=25, ge=2)

    alias = "aroon"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            (params.period + 1) * _LOOKBACK, "high", "low", min_len=params.period + 1
        )
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]

        window_h = highs[-(params.period + 1) :]
        window_l = lows[-(params.period + 1) :]

        bars_since_high = params.period - int(np.argmax(window_h))
        bars_since_low = params.period - int(np.argmin(window_l))

        aroon_up = (params.period - bars_since_high) / params.period * 100.0
        aroon_down = (params.period - bars_since_low) / params.period * 100.0
        return float(aroon_up - aroon_down)

    def __repr__(self) -> str:
        return "Aroon()"
