"""Fisher Transform â€” non-linear normalization of price position."""

from __future__ import annotations

import math

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


class FisherTransform(Indicator):
    """
    Fisher Transform.

    Normalises the close's position within [lowest_low, highest_high] to
    [-0.999, 0.999], then applies the inverse Fisher (logit) transform:
        Fisher = 0.5 * ln((1 + x) / (1 - x))

    Extreme values (|Fisher| > 2) signal exhaustion / likely reversal.
    Returns None when fewer than *period* bars are available or when the
    high-low range is zero.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=10, ge=2)

    alias = "fisher_transform"

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns(params.period, "high", "low", "close")
        if cols is None:
            return None

        highs = cols["high"]
        lows = cols["low"]
        closes = cols["close"]

        hh = float(np.max(highs))
        ll = float(np.min(lows))
        rng = hh - ll
        if rng == 0.0:
            return None

        # Midpoint normalised to [-0.999, 0.999]
        x = 2.0 * (closes[-1] - ll) / rng - 1.0
        x = max(-0.999, min(0.999, x))

        return 0.5 * math.log((1.0 + x) / (1.0 - x))

    def __repr__(self) -> str:
        return "FisherTransform()"
