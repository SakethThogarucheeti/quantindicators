"""Tests for indicators/library/candle_body_ratio.py"""

from __future__ import annotations

import pytest

from quantindicators.library.candle_body_ratio import CandleBodyRatio
from tst.unit.conftest import candles, make_ind


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(CandleBodyRatio, candles([100.0] * 2))
    assert await ind.compute(CandleBodyRatio.Parameters(period=5)) is None


@pytest.mark.asyncio
async def test_in_range() -> None:
    closes = [float(100 + i) for i in range(15)]
    ind = make_ind(CandleBodyRatio, candles(closes))
    result = await ind.compute(CandleBodyRatio.Parameters(period=5))
    assert result is not None
    assert 0.0 <= result <= 1.0


@pytest.mark.asyncio
async def test_returns_float() -> None:
    closes = [float(100 + (i % 3)) for i in range(15)]
    ind = make_ind(CandleBodyRatio, candles(closes))
    result = await ind.compute(CandleBodyRatio.Parameters(period=5))
    assert result is not None
    assert isinstance(result, float)


@pytest.mark.asyncio
async def test_all_doji_returns_none() -> None:
    """All high==low candles → no valid range → None (line 55)."""
    from datetime import UTC, datetime, timedelta
    from unittest.mock import AsyncMock, MagicMock
    from quantindicators.store import AbstractCandleStore

    base = datetime(2024, 1, 1, 9, 15, tzinfo=UTC)
    rows = [
        {
            "symbol": "TEST",
            "interval": "15min",
            "ts": base + timedelta(minutes=15 * i),
            "open": 100.0,
            "high": 100.0,
            "low": 100.0,
            "close": 100.0,
            "volume": 1000,
        }
        for i in range(10)
    ]
    store = MagicMock(spec=AbstractCandleStore)
    store.fetch = AsyncMock(return_value=rows)
    store.fetch_since = AsyncMock(return_value=rows)
    ind = CandleBodyRatio(store, "TEST", "15min")
    assert await ind.compute(CandleBodyRatio.Parameters(period=5)) is None
