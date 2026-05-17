"""Tests for quantindicators store implementations: PolarsStore and BarCachingStore."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from quantindicators.polars_store import PolarsStore
from quantindicators.store import AbstractCandleStore, BarCachingStore


@pytest.mark.asyncio
async def test_polars_store_fetch_returns_empty_for_unknown_symbol() -> None:
    store = PolarsStore()
    result = await store.fetch("UNKNOWN_SYM", "1min", 100)
    assert result == []


@pytest.mark.asyncio
async def test_polars_store_fetch_since_returns_empty_for_unknown_symbol() -> None:
    store = PolarsStore()
    since = datetime(2025, 1, 1, tzinfo=UTC)
    result = await store.fetch_since("UNKNOWN_SYM", "1min", since)
    assert result == []


@pytest.mark.asyncio
async def test_polars_store_push_and_fetch() -> None:
    store = PolarsStore()
    ts = datetime(2024, 1, 1, 9, 15, tzinfo=UTC)
    row = {"symbol": "A", "interval": "1min", "ts": ts, "open": 100.0,
           "high": 101.0, "low": 99.0, "close": 100.5, "volume": 500}
    store.push("A", "1min", row)
    result = await store.fetch("A", "1min", 10)
    assert len(result) == 1
    assert result[0]["close"] == 100.5


@pytest.mark.asyncio
async def test_polars_store_fetch_respects_limit() -> None:
    from datetime import timedelta
    store = PolarsStore()
    base = datetime(2024, 1, 1, 9, 0, tzinfo=UTC)
    for i in range(20):
        ts = base + timedelta(minutes=i)
        store.push("B", "1min", {"symbol": "B", "interval": "1min", "ts": ts,
                                  "open": 1.0, "high": 1.0, "low": 1.0, "close": float(i), "volume": 1})
    result = await store.fetch("B", "1min", 5)
    assert len(result) == 5
    assert result[-1]["close"] == 19.0


@pytest.mark.asyncio
async def test_polars_store_fetch_since_filters_correctly() -> None:
    from datetime import timedelta
    store = PolarsStore()
    base = datetime(2024, 1, 1, 9, 0, tzinfo=UTC)
    for i in range(10):
        ts = base + timedelta(minutes=i)
        store.push("C", "1min", {"symbol": "C", "interval": "1min", "ts": ts,
                                  "open": 1.0, "high": 1.0, "low": 1.0, "close": float(i), "volume": 1})
    since = base + timedelta(minutes=5)
    result = await store.fetch_since("C", "1min", since)
    assert len(result) == 5
    assert all(r["ts"] >= since for r in result)


@pytest.mark.asyncio
async def test_polars_store_respects_maxlen() -> None:
    from datetime import timedelta
    store = PolarsStore(maxlen=5)
    base = datetime(2024, 1, 1, 9, 0, tzinfo=UTC)
    for i in range(10):
        ts = base + timedelta(minutes=i)
        store.push("D", "1min", {"symbol": "D", "interval": "1min", "ts": ts,
                                  "open": 1.0, "high": 1.0, "low": 1.0, "close": float(i), "volume": 1})
    result = await store.fetch("D", "1min", 100)
    assert len(result) == 5
    assert result[0]["close"] == 5.0  # oldest kept is index 5


# ---------------------------------------------------------------------------
# BarCachingStore
# ---------------------------------------------------------------------------


def _make_inner(rows: list) -> AbstractCandleStore:
    inner = MagicMock(spec=AbstractCandleStore)
    inner.fetch = AsyncMock(return_value=rows)
    inner.fetch_since = AsyncMock(return_value=rows)
    return inner


@pytest.mark.asyncio
async def test_bar_caching_store_deduplicates_fetch() -> None:
    rows = [{"close": 1.0}]
    inner = _make_inner(rows)
    store = BarCachingStore(inner)

    r1 = await store.fetch("INFY", "15min", 10)
    r2 = await store.fetch("INFY", "15min", 10)

    assert r1 == r2 == rows
    inner.fetch.assert_called_once()  # only one real call despite two fetches


@pytest.mark.asyncio
async def test_bar_caching_store_deduplicates_fetch_since() -> None:
    rows = [{"close": 2.0}]
    inner = _make_inner(rows)
    store = BarCachingStore(inner)
    since = datetime(2024, 1, 1, tzinfo=UTC)

    r1 = await store.fetch_since("INFY", "15min", since)
    r2 = await store.fetch_since("INFY", "15min", since)

    assert r1 == r2 == rows
    inner.fetch_since.assert_called_once()


@pytest.mark.asyncio
async def test_bar_caching_store_invalidate_clears_cache() -> None:
    rows = [{"close": 3.0}]
    inner = _make_inner(rows)
    store = BarCachingStore(inner)

    await store.fetch("INFY", "15min", 10)
    store.invalidate()
    await store.fetch("INFY", "15min", 10)

    assert inner.fetch.call_count == 2  # second fetch hit the inner store again


@pytest.mark.asyncio
async def test_bar_caching_store_different_keys_not_deduplicated() -> None:
    inner = _make_inner([])
    store = BarCachingStore(inner)

    await store.fetch("INFY", "15min", 10)
    await store.fetch("INFY", "15min", 20)  # different limit
    await store.fetch("TCS", "15min", 10)   # different symbol

    assert inner.fetch.call_count == 3
