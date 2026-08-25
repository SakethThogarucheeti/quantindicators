"""Shared helper: standard EMA over a full array, for indicators needing the series."""

from __future__ import annotations

import numpy as np


def ema_series(values: np.ndarray, period: int) -> np.ndarray:
    """Standard EMA (alpha = 2/(period+1)) over an array, returns full array."""
    alpha = 2.0 / (period + 1)
    out = np.empty(len(values))
    out[0] = values[0]
    for i in range(1, len(values)):
        out[i] = alpha * values[i] + (1.0 - alpha) * out[i - 1]
    return out
