"""TrueRange â€” True Range as a standalone indicator (returns latest TR value)."""

from __future__ import annotations

import numpy as np

from quantindicators.base import Indicator, IndicatorParameters


def true_range(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> np.ndarray:
    """
    True Range array for an OHLCV sequence.

    TR[0] = high[0] - low[0]  (no previous close)
    TR[i] = max(H-L, |H-Cprev|, |L-Cprev|)
    """
    hl = highs - lows
    prev_close = np.empty_like(closes)
    prev_close[0] = closes[0]
    prev_close[1:] = closes[:-1]
    hc = np.abs(highs - prev_close)
    lc = np.abs(lows - prev_close)
    return np.maximum(hl, np.maximum(hc, lc))


class TrueRange(Indicator):
    """
    True Range for the most recent bar.

    TR = max(H-L, |H-Cprev|, |L-Cprev|)

    Returns None when fewer than 2 bars are available (need at least one
    previous close to compute the gap components).
    """

    class Parameters(IndicatorParameters):
        pass

    alias = "true_range"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(2, "high", "low", "close")
        if cols is None:
            return None
        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]
        tr = true_range(highs, lows, closes)
        return float(tr[-1])

    def __repr__(self) -> str:
        return "TrueRange()"
