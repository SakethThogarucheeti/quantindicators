"""VWAP Bands — session VWAP with standard deviation bands."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np
from pydantic import Field

from quantindicators.base import Indicator, IndicatorParameters

if TYPE_CHECKING:
    from quantindicators.store import AbstractCandleStore


class VWAPBands(Indicator):
    """
    VWAP Bands — like Bollinger Bands but anchored to the session VWAP.

    Upper = VWAP + num_std * std(close - VWAP)
    Lower = VWAP - num_std * std(close - VWAP)
    %B    = (close - lower) / (upper - lower)

    Returns %B in [0, 1] approximately; > 1 or < 0 possible on extremes.
    Returns None if session has < 2 bars or upper == lower.
    The caller is responsible for computing session_open_utc.
    """

    class Parameters(IndicatorParameters):
        session_open_utc: datetime
        num_std: float = Field(default=2.0, gt=0)

    alias = "vwap_bands"

    async def compute(self, params: Parameters) -> float | None:  # type: ignore[override]
        rows = await self._store.fetch_since(self._symbol, self._interval, params.session_open_utc)
        if len(rows) < 2:
            return None

        closes = np.array([r["close"] for r in rows], dtype=float)
        volumes = np.array([r["volume"] for r in rows], dtype=float)

        total_vol = float(volumes.sum())
        if total_vol == 0.0:
            return None

        vwap = float((closes * volumes).sum() / total_vol)
        deviations = closes - vwap
        std = float(np.std(deviations, ddof=1))

        if std == 0.0:
            return None

        upper = vwap + params.num_std * std
        lower = vwap - params.num_std * std
        band_width = upper - lower
        if band_width == 0.0:
            return None

        return (closes[-1] - lower) / band_width

    def __repr__(self) -> str:
        return "VWAPBands()"
