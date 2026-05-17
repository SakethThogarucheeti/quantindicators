"""Session VWAP — cumulative volume-weighted average price from today's 09:15 IST open."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import numpy as np

from quantindicators.base import Indicator, IndicatorParameters

if TYPE_CHECKING:
    from quantindicators.store import AbstractCandleStore


class VWAP(Indicator):
    """
    Cumulative session VWAP for the current trading day.

    Fetches all candles from today's session open onward via ``fetch_since()``.
    The caller is responsible for computing the session open datetime and passing
    it as ``params.session_open_utc``. Returns None when no bars have been
    ingested for the current session or total volume is zero.
    """

    class Parameters(IndicatorParameters):
        session_open_utc: datetime

    alias = "vwap"

    async def compute(self, params: Parameters) -> float | None:  # type: ignore[override]
        rows = await self._store.fetch_since(self._symbol, self._interval, params.session_open_utc)
        if not rows:
            return None

        closes = np.array([r["close"] for r in rows], dtype=float)
        volumes = np.array([r["volume"] for r in rows], dtype=float)

        total_vol = volumes.sum()
        if total_vol == 0.0:
            return None

        return float((closes * volumes).sum() / total_vol)

    def __repr__(self) -> str:
        return "VWAP()"
