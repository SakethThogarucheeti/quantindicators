"""Session VWAP — cumulative volume-weighted average price from today's 09:15 IST open."""

from __future__ import annotations

from datetime import datetime

from quantindicators.base import Indicator, IndicatorParameters


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

    async def compute(self, params: Parameters) -> float | None:
        cols = await self._fetch_columns_since(
            params.session_open_utc, "close", "volume", min_len=1
        )
        if cols is None:
            return None

        closes = cols["close"]
        volumes = cols["volume"]

        total_vol = volumes.sum()
        if total_vol == 0.0:
            return None

        return float((closes * volumes).sum() / total_vol)

    def __repr__(self) -> str:
        return "VWAP()"
