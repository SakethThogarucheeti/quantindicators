"""WilderEMA â€” Wilder's exponential moving average as a standalone indicator."""

from __future__ import annotations

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

_LOOKBACK_FACTOR = 3


def wilder_ema(values: np.ndarray, period: int) -> float:
    """
    Wilder's EMA (alpha = 1/period) over ``values``.

    Equivalent to Polars ewm_mean(alpha=1/period, adjust=False)[-1].
    Uses scipy.signal.lfilter for a single vectorised pass.
    Requires quantindicators[scipy] to be installed.
    """
    try:
        from scipy.signal import lfilter  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "wilder_ema requires scipy. Install with: pip install quantindicators[scipy]"
        ) from exc
    alpha = 1.0 / period
    b = [alpha]
    a = [1.0, -(1.0 - alpha)]
    zi = np.array([values[0] * (1.0 - alpha)])
    out, _ = lfilter(b, a, values, zi=zi)
    return float(out[-1])


async def wilder_ema_of_close(
    indicator: Indicator, period: int, lookback_factor: int = _LOOKBACK_FACTOR
) -> float | None:
    """
    Shared fetch-and-smooth path for indicators whose value is simply
    ``wilder_ema(closes, period)`` (currently: EMA and WilderEMA itself,
    which are the same formula under two aliases).
    """
    cols = await indicator._fetch_columns(
        period * lookback_factor, "close", min_len=period
    )
    if cols is None:
        return None
    return wilder_ema(cols["close"], period)


class WilderEMA(Indicator):
    """
    Wilder's EMA (alpha = 1/period) applied to the close price.

    Distinct from the standard EMA in that alpha = 1/period rather than
    2/(period+1). Used internally by RSI and ATR; also useful directly
    when you want the same smoothing characteristic as those indicators.

    Returns None when fewer than *period* bars are available.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=14, ge=1)

    alias = "wilder_ema"

    async def compute(self, params: Parameters) -> float | None:
        return await wilder_ema_of_close(self, params.period)

    def __repr__(self) -> str:
        return "WilderEMA()"
