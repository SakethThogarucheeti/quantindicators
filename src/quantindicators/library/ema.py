"""Exponential Moving Average (Wilder smoothing)."""

from __future__ import annotations

from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.wilder_ema import wilder_ema_of_close


class EMA(Indicator):
    """
    Wilder EMA with configurable period.

    alpha = 1 / period  (consistent with TechnicalFeatureEngine and Polars
    ewm_mean(span=period, adjust=False)).

    Returns None when fewer than *period* bars are available.
    """

    class Parameters(IndicatorParameters):
        period: int = Field(default=9, ge=1)

    alias = "ema"

    async def compute(self, params: Parameters) -> float | None:
        return await wilder_ema_of_close(self, params.period)

    def __repr__(self) -> str:
        return "EMA()"
