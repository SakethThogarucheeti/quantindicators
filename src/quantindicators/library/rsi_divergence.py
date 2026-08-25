"""RSI Divergence â€” bullish when price makes new low but RSI does not."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.rsi_series import rsi_series as _rsi_series

if TYPE_CHECKING:
    pass

_LOOKBACK = 3


class RSIDivergence(Indicator):
    """
    RSI Divergence score.

    Measures the difference between the normalised price change and
    the normalised RSI change over a lookback window:

        price_chg  = (close_now - close_N_ago) / close_N_ago
        rsi_chg    = (rsi_now  - rsi_N_ago)  / 100
        divergence = rsi_chg - price_chg

    Positive value â†’ bullish divergence (RSI stronger than price â†’ mean reversion up).
    Negative value â†’ bearish divergence.

    Returns None when insufficient bars.
    """

    class Parameters(IndicatorParameters):
        rsi_period: int = Field(default=14, ge=2)
        divergence_window: int = Field(default=10, ge=2)

    alias = "rsi_divergence"

    async def compute(self, params: Parameters) -> float | None:
        needed = (params.rsi_period + params.divergence_window) * _LOOKBACK
        rows = await self._store.fetch(self._symbol, self._interval, needed)
        if len(rows) < params.rsi_period + params.divergence_window + 1:
            return None

        closes = np.array([r["close"] for r in rows], dtype=float)
        rsi = _rsi_series(closes, params.rsi_period)

        # Need at least divergence_window valid RSI values
        valid_idx = np.where(~np.isnan(rsi))[0]
        if len(valid_idx) < params.divergence_window:
            return None

        now_idx = valid_idx[-1]
        ago_idx = valid_idx[-params.divergence_window]

        close_now = closes[now_idx]
        close_ago = closes[ago_idx]
        if close_ago == 0:
            return None

        price_chg = (close_now - close_ago) / close_ago
        rsi_chg = (rsi[now_idx] - rsi[ago_idx]) / 100.0

        return float(rsi_chg - price_chg)

    def __repr__(self) -> str:
        return "RSIDivergence()"
