"""Tests for indicators/library/connors_rsi.py"""

from __future__ import annotations

import pytest

from quantindicators.library.connors_rsi import ConnorsRSI
from tst.unit.conftest import candles, make_ind


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(ConnorsRSI, candles([100.0] * 5))
    assert (
        await ind.compute(ConnorsRSI.Parameters(rsi_period=3, streak_period=2, rank_period=100))
        is None
    )


@pytest.mark.asyncio
async def test_in_range() -> None:
    closes = [float(100 + (i % 7)) for i in range(200)]
    ind = make_ind(ConnorsRSI, candles(closes))
    result = await ind.compute(
        ConnorsRSI.Parameters(rsi_period=3, streak_period=2, rank_period=100)
    )
    assert result is not None
    assert 0.0 <= result <= 100.0


@pytest.mark.asyncio
async def test_returns_float() -> None:
    closes = [float(100 + (i % 7) * 0.5) for i in range(400)]
    ind = make_ind(ConnorsRSI, candles(closes))
    result = await ind.compute(ConnorsRSI.Parameters())
    assert result is not None
    assert isinstance(result, float)


@pytest.mark.asyncio
async def test_flat_price_returns_none() -> None:
    """Constant price → avg_loss == 0 → None at price_rsi branch (line 59)."""
    closes = [100.0] * 50
    ind = make_ind(ConnorsRSI, candles(closes))
    result = await ind.compute(ConnorsRSI.Parameters(rsi_period=3, streak_period=2, rank_period=10))
    assert result is None


@pytest.mark.asyncio
async def test_streak_period_too_large_returns_none() -> None:
    """streak_period larger than available streak data → None (line 76)."""
    closes = [float(100 + (i % 3)) for i in range(30)]
    ind = make_ind(ConnorsRSI, candles(closes))
    result = await ind.compute(ConnorsRSI.Parameters(rsi_period=3, streak_period=50, rank_period=5))
    assert result is None


@pytest.mark.asyncio
async def test_rank_period_too_large_returns_none() -> None:
    """rank_period larger than data → None (line 87)."""
    closes = [float(100 + (i % 5)) for i in range(50)]
    ind = make_ind(ConnorsRSI, candles(closes))
    result = await ind.compute(ConnorsRSI.Parameters(rsi_period=3, streak_period=2, rank_period=500))
    assert result is None
