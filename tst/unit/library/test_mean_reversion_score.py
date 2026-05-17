"""Tests for indicators/library/mean_reversion_score.py"""

from __future__ import annotations

import pytest

from quantindicators.library.mean_reversion_score import MeanReversionScore
from tst.unit.conftest import candles, make_ind


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(MeanReversionScore, candles([100.0] * 5))
    assert await ind.compute(MeanReversionScore.Parameters(period=20, rsi_period=14)) is None


@pytest.mark.asyncio
async def test_in_range() -> None:
    closes = [float(100 + (i % 7)) for i in range(80)]
    ind = make_ind(MeanReversionScore, candles(closes))
    result = await ind.compute(MeanReversionScore.Parameters(period=20, rsi_period=14))
    assert result is not None
    assert 0.0 <= result <= 100.0


@pytest.mark.asyncio
async def test_overbought_has_high_score() -> None:
    closes = [float(100 + i * 2) for i in range(80)]
    ind = make_ind(MeanReversionScore, candles(closes))
    result = await ind.compute(MeanReversionScore.Parameters(period=20, rsi_period=14))
    assert result is not None
    assert result > 50.0


@pytest.mark.asyncio
async def test_rsi_period_larger_than_data_returns_none() -> None:
    """rsi_period > available data → _rsi_scalar returns None → None (line 81)."""
    closes = [float(100 + (i % 5)) for i in range(30)]
    ind = make_ind(MeanReversionScore, candles(closes))
    result = await ind.compute(MeanReversionScore.Parameters(period=10, rsi_period=500))
    assert result is None


@pytest.mark.asyncio
async def test_flat_price_std_zero_returns_none() -> None:
    """All prices identical → std == 0 → None (line 74)."""
    closes = [100.0] * 80
    ind = make_ind(MeanReversionScore, candles(closes))
    result = await ind.compute(MeanReversionScore.Parameters(period=20, rsi_period=3))
    assert result is None
