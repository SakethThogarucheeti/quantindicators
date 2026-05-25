"""AbstractCandleStore — interface all indicators depend on for OHLCV data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from quantindicators.types import CandleRow


class AbstractCandleStore(ABC):
    """Common interface for all candle data sources."""

    @abstractmethod
    async def fetch(self, symbol: str, interval: str, limit: int) -> list[CandleRow]:
        """Return the last *limit* candles ordered ts ASC (oldest→newest)."""

    @abstractmethod
    async def fetch_since(self, symbol: str, interval: str, since: datetime) -> list[CandleRow]:
        """Return all candles with ts >= *since*, ordered ts ASC."""
