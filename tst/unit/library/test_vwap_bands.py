"""Tests for quantindicators/library/vwap_bands.py"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from quantindicators.library.vwap_bands import VWAPBands
from quantindicators.store import AbstractCandleStore
from tst.unit.conftest import candles, make_store

_SESSION_OPEN = datetime(2024, 1, 1, 3, 45, tzinfo=UTC)  # 09:15 IST as UTC


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    store = make_store(candles([100.0]))
    ind = VWAPBands(store, "TEST", "15min")
    assert await ind.compute(VWAPBands.Parameters(session_open_utc=_SESSION_OPEN)) is None


@pytest.mark.asyncio
async def test_returns_float() -> None:
    rows = candles([float(100 + i) for i in range(10)])
    store = make_store(rows)
    ind = VWAPBands(store, "TEST", "15min")
    result = await ind.compute(VWAPBands.Parameters(session_open_utc=_SESSION_OPEN, num_std=2.0))
    assert result is not None
    assert isinstance(result, float)


@pytest.mark.asyncio
async def test_zero_volume_returns_none() -> None:
    base = datetime(2024, 1, 1, 3, 45, tzinfo=UTC)
    rows = [
        {
            "symbol": "TEST", "interval": "15min",
            "ts": base + timedelta(minutes=15 * i),
            "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.0, "volume": 0,
        }
        for i in range(10)
    ]
    store = MagicMock(spec=AbstractCandleStore)
    store.fetch_since = AsyncMock(return_value=rows)
    store.fetch = AsyncMock(return_value=rows)
    ind = VWAPBands(store, "TEST", "15min")
    assert await ind.compute(VWAPBands.Parameters(session_open_utc=_SESSION_OPEN)) is None
