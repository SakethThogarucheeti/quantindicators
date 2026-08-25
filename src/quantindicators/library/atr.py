"""Average True Range (Wilder smoothing)."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.true_range import true_range
from quantindicators.library.wilder_ema import wilder_ema

_LOOKBACK_FACTOR = 3


class ATR(Indicator):
    """
    Average True Range with Wilder smoothing (alpha = 1/period).

    True Range = max(H-L, |H-Cprev|, |L-Cprev|)

    Returns None when fewer than *period* bars are available.
    Returns None when the computed ATR is zero (no price movement â€” stop
    distance would be zero, making position sizing undefined).
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=14, ge=1)

    alias = "atr"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(
            params.period * _LOOKBACK_FACTOR, "high", "low", "close", min_len=params.period
        )
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]

        tr = true_range(highs, lows, closes)
        atr = wilder_ema(tr, params.period)
        return float(atr) if atr > 0 else None

    def __repr__(self) -> str:
        return "ATR()"
