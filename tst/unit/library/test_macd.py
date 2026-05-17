"""Tests for indicators/library/macd.py"""

from __future__ import annotations

import math

import pytest

from quantindicators.library.macd import MACD
from tst.unit.conftest import candles, make_ind


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(MACD, candles([100.0] * 10))
    assert await ind.compute(MACD.Parameters(fast=12, slow=26, signal=9)) is None


@pytest.mark.asyncio
async def test_fast_gte_slow_returns_none() -> None:
    ind = make_ind(MACD, candles([100.0] * 80))
    assert await ind.compute(MACD.Parameters(fast=26, slow=12)) is None


@pytest.mark.asyncio
async def test_uptrend_positive() -> None:
    closes = [float(100 + i) for i in range(80)]
    ind = make_ind(MACD, candles(closes))
    result = await ind.compute(MACD.Parameters(fast=12, slow=26, signal=9))
    assert result is not None
    assert result > 0.0


@pytest.mark.asyncio
async def test_compute_full_returns_three_values() -> None:
    closes = [float(100 + i) for i in range(80)]
    ind = make_ind(MACD, candles(closes))
    result = await ind.compute_full(MACD.Parameters(fast=12, slow=26, signal=9))
    assert result is not None
    macd, signal, hist = result
    assert math.isclose(macd - signal, hist, rel_tol=1e-9)


@pytest.mark.asyncio
async def test_signal_period_too_large_returns_none() -> None:
    """macd_series shorter than signal period → None (line 71)."""
    # 30 candles: enough for slow EMA but macd_series will be short vs a huge signal
    closes = [float(100 + i) for i in range(30)]
    ind = make_ind(MACD, candles(closes))
    result = await ind.compute(MACD.Parameters(fast=5, slow=10, signal=100))
    assert result is None
