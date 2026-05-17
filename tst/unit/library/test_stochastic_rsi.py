"""Tests for indicators/library/stochastic_rsi.py"""

from __future__ import annotations

import pytest

from quantindicators.library.stochastic_rsi import StochasticRSI
from tst.unit.conftest import candles, make_ind


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(StochasticRSI, candles([100.0] * 5))
    assert await ind.compute(StochasticRSI.Parameters(rsi_period=14, stoch_period=14)) is None


@pytest.mark.asyncio
async def test_in_range() -> None:
    closes = [float(100 + (i % 7)) for i in range(100)]
    ind = make_ind(StochasticRSI, candles(closes))
    result = await ind.compute(StochasticRSI.Parameters(rsi_period=14, stoch_period=14))
    assert result is not None
    assert 0.0 <= result <= 100.0


@pytest.mark.asyncio
async def test_returns_float() -> None:
    closes = [float(100 + (i % 7) * 0.5) for i in range(150)]
    ind = make_ind(StochasticRSI, candles(closes))
    result = await ind.compute(StochasticRSI.Parameters())
    assert result is not None
    assert isinstance(result, float)


@pytest.mark.asyncio
async def test_stoch_period_too_large_returns_none() -> None:
    """Not enough valid RSI values for stoch_period → None (line 71)."""
    closes = [float(100 + (i % 3)) for i in range(20)]
    ind = make_ind(StochasticRSI, candles(closes))
    result = await ind.compute(StochasticRSI.Parameters(rsi_period=3, stoch_period=100))
    assert result is None


@pytest.mark.asyncio
async def test_flat_rsi_returns_none() -> None:
    """RSI min == max (flat) → hi == lo → None (line 76)."""
    # All prices the same → RSI locked at 100 for all periods → hi == lo
    closes = [100.0] * 40
    ind = make_ind(StochasticRSI, candles(closes))
    result = await ind.compute(StochasticRSI.Parameters(rsi_period=3, stoch_period=5))
    assert result is None
