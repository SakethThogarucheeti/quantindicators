"""Tests for indicators/library/adx.py"""

from __future__ import annotations

import pytest

from quantindicators.library.adx import ADX
from tst.unit.conftest import candles, make_ind


def _ref_wilder_ema(values: list[float], period: int) -> list[float]:
    """Independent (pure-Python, non-vectorised) reference for the same
    recursion wilder_ema() implements via scipy.signal.lfilter: y[0] = x[0],
    y[n] = alpha*x[n] + (1-alpha)*y[n-1] with alpha = 1/period (equivalent to
    pandas/Polars ewm(adjust=False)). Used to independently cross-check ADX's
    Wilder-smoothing of DX without reusing the production implementation."""
    alpha = 1.0 / period
    y = values[0]
    out = [y]
    for v in values[1:]:
        y = alpha * v + (1.0 - alpha) * y
        out.append(y)
    return out


def _ref_adx(closes: list[float], highs: list[float], lows: list[float], period: int) -> float:
    """Independent reference ADX: builds the per-bar DX series from raw OHLC
    and Wilder-smooths it over `period`, mirroring what compute_full should
    do (as opposed to the old bug, which returned the single latest DX)."""
    n = len(closes)
    tr = [highs[0] - lows[0]]
    for i in range(1, n):
        prev_close = closes[i - 1]
        tr.append(max(highs[i] - lows[i], abs(highs[i] - prev_close), abs(lows[i] - prev_close)))

    plus_dm = []
    minus_dm = []
    for i in range(1, n):
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]
        plus_dm.append(up_move if (up_move > down_move and up_move > 0) else 0.0)
        minus_dm.append(down_move if (down_move > up_move and down_move > 0) else 0.0)

    smoothed_tr = _ref_wilder_ema(tr[1:], period)
    smoothed_plus = _ref_wilder_ema(plus_dm, period)
    smoothed_minus = _ref_wilder_ema(minus_dm, period)

    dx_series = []
    for i in range(len(smoothed_tr)):
        if smoothed_tr[i] == 0.0:
            dx_series.append(0.0)
            continue
        plus_di = 100.0 * smoothed_plus[i] / smoothed_tr[i]
        minus_di = 100.0 * smoothed_minus[i] / smoothed_tr[i]
        di_sum = plus_di + minus_di
        dx_series.append(100.0 * abs(plus_di - minus_di) / di_sum if di_sum != 0.0 else 0.0)

    return _ref_wilder_ema(dx_series, period)[-1]


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    ind = make_ind(ADX, candles([100.0] * 10))
    assert await ind.compute(ADX.Parameters(period=14)) is None


@pytest.mark.asyncio
async def test_in_range() -> None:
    closes = [float(100 + (i % 7)) for i in range(60)]
    ind = make_ind(ADX, candles(closes))
    result = await ind.compute(ADX.Parameters(period=14))
    assert result is not None
    assert 0.0 <= result <= 100.0


@pytest.mark.asyncio
async def test_full_returns_three() -> None:
    closes = [float(100 + i) for i in range(60)]
    ind = make_ind(ADX, candles(closes))
    result = await ind.compute_full(ADX.Parameters(period=14))
    assert result is not None
    adx, plus_di, minus_di = result
    assert adx >= 0.0
    assert plus_di >= 0.0
    assert minus_di >= 0.0


@pytest.mark.asyncio
async def test_flat_price_returns_none() -> None:
    """Constant price → smoothed_tr = 0 → None (line 68)."""
    ind = make_ind(ADX, candles([100.0] * 40))
    assert await ind.compute(ADX.Parameters(period=14)) is None


@pytest.mark.asyncio
async def test_adx_matches_wilder_smoothed_dx_reference() -> None:
    """Regression test for the bug fixed in quantindicators#14: adx used to
    be the raw single-bar DX reading instead of the Wilder EMA of the DX
    series. Cross-checks compute_full()'s adx against an independent
    (non-vectorised) reference implementation of the correct formula."""
    period = 14
    closes = [100.0 + 3.0 * ((i * 37) % 11 - 5) + 0.4 * i for i in range(60)]
    rows = candles(closes)
    highs = [r["high"] for r in rows]
    lows = [r["low"] for r in rows]

    ind = make_ind(ADX, rows)
    result = await ind.compute_full(ADX.Parameters(period=period))
    assert result is not None
    adx, _plus_di, _minus_di = result

    expected = _ref_adx(closes, highs, lows, period)
    assert adx == pytest.approx(expected, rel=1e-9)


@pytest.mark.asyncio
async def test_adx_is_not_raw_single_bar_dx() -> None:
    """The pre-fix bug returned adx == dx (the unsmoothed single-bar reading).
    A trending-then-reversing series makes the smoothed and raw values
    diverge, so this catches a regression back to the old behavior."""
    closes = [100.0 + i for i in range(30)] + [130.0 - i for i in range(30)]
    ind = make_ind(ADX, candles(closes))
    result = await ind.compute_full(ADX.Parameters(period=14))
    assert result is not None
    adx, plus_di, minus_di = result

    raw_dx = 100.0 * abs(plus_di - minus_di) / (plus_di + minus_di)
    assert adx != pytest.approx(raw_dx)
