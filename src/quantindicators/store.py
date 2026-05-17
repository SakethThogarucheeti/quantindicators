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


class BarCachingStore(AbstractCandleStore):
    """Wraps any AbstractCandleStore and deduplicates fetch calls within a single bar.

    Call invalidate() once per bar before running indicators. All indicators
    sharing this instance will hit the cache for identical (symbol, interval, limit)
    calls — only one real fetch reaches the underlying store.
    """

    def __init__(self, inner: AbstractCandleStore) -> None:
        self._inner = inner
        self._cache: dict[tuple[str, ...], list[CandleRow]] = {}

    def invalidate(self) -> None:
        self._cache.clear()

    async def fetch(self, symbol: str, interval: str, limit: int) -> list[CandleRow]:
        key = ("fetch", symbol, interval, str(limit))
        if key not in self._cache:
            self._cache[key] = await self._inner.fetch(symbol, interval, limit)
        return self._cache[key]

    async def fetch_since(self, symbol: str, interval: str, since: datetime) -> list[CandleRow]:
        key = ("fetch_since", symbol, interval, since.isoformat())
        if key not in self._cache:
            self._cache[key] = await self._inner.fetch_since(symbol, interval, since)
        return self._cache[key]
