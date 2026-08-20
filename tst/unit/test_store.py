"""Tests for quantindicators store implementations: PolarsStore."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from quantindicators.polars_store import PolarsStore


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
async def test_polars_store_push_same_ts_replaces_not_appends() -> None:
    """
    Regression: redelivery of the same bar (e.g. a live feed replaying a
    warmup-seeded candle again right after startup replay) must not create
    a duplicate entry — every downstream indicator (RSI/ATR/EMA) weights by
    position in the window, so a silent duplicate biases the result.
    """
    store = PolarsStore()
    ts = datetime(2024, 1, 1, 9, 15, tzinfo=UTC)
    first = {"symbol": "E", "interval": "1min", "ts": ts, "open": 100.0,
             "high": 101.0, "low": 99.0, "close": 100.5, "volume": 500}
    redelivered = {"symbol": "E", "interval": "1min", "ts": ts, "open": 100.0,
                   "high": 101.0, "low": 99.0, "close": 100.5, "volume": 500}
    store.push("E", "1min", first)
    store.push("E", "1min", redelivered)
    result = await store.fetch("E", "1min", 10)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_polars_store_push_same_ts_uses_latest_values() -> None:
    """A redelivered bar with revised OHLC replaces the stale copy in place."""
    store = PolarsStore()
    ts = datetime(2024, 1, 1, 9, 15, tzinfo=UTC)
    store.push("F", "1min", {"symbol": "F", "interval": "1min", "ts": ts, "open": 100.0,
                              "high": 101.0, "low": 99.0, "close": 100.5, "volume": 500})
    store.push("F", "1min", {"symbol": "F", "interval": "1min", "ts": ts, "open": 100.0,
                              "high": 102.0, "low": 99.0, "close": 101.0, "volume": 900})
    result = await store.fetch("F", "1min", 10)
    assert len(result) == 1
    assert result[0]["close"] == 101.0
    assert result[0]["volume"] == 900


@pytest.mark.asyncio
async def test_polars_store_push_different_ts_still_appends() -> None:
    store = PolarsStore()
    base = datetime(2024, 1, 1, 9, 0, tzinfo=UTC)
    from datetime import timedelta
    store.push("G", "1min", {"symbol": "G", "interval": "1min", "ts": base,
                              "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1})
    store.push("G", "1min", {"symbol": "G", "interval": "1min", "ts": base + timedelta(minutes=1),
                              "open": 1.0, "high": 1.0, "low": 1.0, "close": 2.0, "volume": 1})
    result = await store.fetch("G", "1min", 10)
    assert len(result) == 2


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
