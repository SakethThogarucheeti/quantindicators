"""Tests for indicators/library/stochastic.py"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from quantindicators.library.stochastic import Stochastic
from quantindicators.store import AbstractCandleStore
from tst.unit.conftest import candles, make_ind


def _store(rows):
    s = MagicMock(spec=AbstractCandleStore)
    s.fetch = AsyncMock(return_value=rows)
    s.fetch_since = AsyncMock(return_value=rows)
    return s


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(Stochastic, candles([100.0] * 5))
    assert await ind.compute(Stochastic.Parameters(k_period=14)) is None


@pytest.mark.asyncio
async def test_in_range() -> None:
    closes = [float(100 + (i % 10)) for i in range(30)]
    ind = make_ind(Stochastic, candles(closes))
    result = await ind.compute(Stochastic.Parameters(k_period=14, d_period=3))
    assert result is not None
    assert 0.0 <= result <= 100.0


@pytest.mark.asyncio
async def test_at_high_is_100() -> None:
    rows = candles([100.0] * 13 + [110.0])
    for r in rows:
        r["high"] = r["close"] + 0.0
        r["low"] = r["close"] - 5.0
    rows[-1]["high"] = 110.0
    rows[-1]["low"] = 105.0
    ind = Stochastic(_store(rows), "TEST", "15min")
    result = await ind.compute(Stochastic.Parameters(k_period=14, d_period=3))
    assert result is not None
    assert result == pytest.approx(100.0, abs=1e-6)


@pytest.mark.asyncio
async def test_flat_price_returns_midpoint() -> None:
    """Flat price → high == low → k_value = 50.0 (line 61)."""
    from datetime import UTC, datetime, timedelta
    from unittest.mock import AsyncMock, MagicMock
    from quantindicators.store import AbstractCandleStore

    base = datetime(2024, 1, 1, 9, 15, tzinfo=UTC)
    rows = [
        {
            "symbol": "TEST", "interval": "15min",
            "ts": base + timedelta(minutes=15 * i),
            "open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1000,
        }
        for i in range(20)
    ]
    store = MagicMock(spec=AbstractCandleStore)
    store.fetch = AsyncMock(return_value=rows)
    store.fetch_since = AsyncMock(return_value=rows)
    ind = Stochastic(store, "TEST", "15min")
    result = await ind.compute(Stochastic.Parameters(k_period=14))
    assert result == 50.0
