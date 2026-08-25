"""MACD â€” Moving Average Convergence/Divergence."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters


def _ema_standard(values: np.ndarray, period: int) -> float:
    """Standard EMA (alpha = 2/(period+1)), not Wilder's."""
    alpha = 2.0 / (period + 1)
    acc = values[0]
    for v in values[1:]:
        acc = alpha * v + (1.0 - alpha) * acc
    return acc


class MACD(Indicator):
    """
    MACD line, signal line, and histogram.

    MACD line  = EMA(fast) - EMA(slow)   [standard alpha = 2/(n+1)]
    Signal     = EMA(MACD line, signal_period)
    Histogram  = MACD - Signal

    Returns (macd, signal, histogram) or None when insufficient data.
    Uses compute() â†’ float for the MACD line; use compute_full() for all three.
    """

    class Parameters(IndicatorParameters):
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)

    alias = "macd"

    async def compute(self, params: Parameters) -> float | None:
        result = await self.compute_full(params)
        return result[0] if result is not None else None

    async def compute_full(self, params: Parameters) -> tuple[float, float, float] | None:
        if params.fast >= params.slow:
            return None
        limit = params.slow * 3 + params.signal
        cols = await self._fetch_columns(limit, "close", min_len=params.slow + params.signal)
        if cols is None:
            return None

        closes = cols["close"]

        # Build MACD line over a rolling window so we have enough points
        # to smooth into a signal line.
        macd_series: list[float] = []
        for i in range(params.slow - 1, len(closes)):
            window = closes[: i + 1]
            fast_val = _ema_standard(window[-params.fast * 3 :], params.fast)
            slow_val = _ema_standard(window[-params.slow * 3 :], params.slow)
            macd_series.append(fast_val - slow_val)

        if len(macd_series) < params.signal:
            return None

        macd_arr = np.array(macd_series, dtype=float)
        macd_line = macd_arr[-1]
        signal_line = _ema_standard(macd_arr[-params.signal * 3 :], params.signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def __repr__(self) -> str:
        return "MACD()"
