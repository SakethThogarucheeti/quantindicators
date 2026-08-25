"""Linear Regression Slope â€” trend strength without lag."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK = 2


class LinearRegressionSlope(Indicator):
    """
    Linear Regression Slope.

    Fits a least-squares line to the last *period* closes and returns
    the slope normalised by the mean price (so it's comparable across symbols):

        slope_pct = slope / mean(closes) * 100

    Positive â†’ uptrend. Negative â†’ downtrend.
    Signal extractor: as-is for trend, negate for mean reversion.

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=20, ge=3)

    alias = "linreg_slope"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period * _LOOKBACK, "close", min_len=params.period)
        if cols is None:
            return None

        closes = cols["close"][-params.period :]
        x = np.arange(params.period, dtype=float)
        x -= x.mean()
        slope = float(np.dot(x, closes) / np.dot(x, x))
        mean_price = float(np.mean(closes))
        if mean_price == 0:
            return None
        return float(slope / mean_price * 100.0)

    def __repr__(self) -> str:
        return "LinearRegressionSlope()"
