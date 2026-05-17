"""Tests for quantindicators/library/session_high_low_pct.py"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from quantindicators.library.session_high_low_pct import SessionHighLowPct
from tst.unit.conftest import candles, make_store

_SESSION_OPEN = datetime(2024, 1, 1, 3, 45, tzinfo=UTC)  # 09:15 IST as UTC


@pytest.mark.asyncio
async def test_returns_none_insufficient() -> None:
    store = make_store(candles([100.0]))
    ind = SessionHighLowPct(store, "TEST", "15min")
    assert await ind.compute(SessionHighLowPct.Parameters(session_open_utc=_SESSION_OPEN)) is None


@pytest.mark.asyncio
async def test_in_range() -> None:
    rows = candles([float(100 + i) for i in range(10)])
    store = make_store(rows)
    ind = SessionHighLowPct(store, "TEST", "15min")
    result = await ind.compute(SessionHighLowPct.Parameters(session_open_utc=_SESSION_OPEN))
    assert result is not None
    assert 0.0 <= result <= 1.0


@pytest.mark.asyncio
async def test_at_session_low_gives_zero() -> None:
    rows = candles([100.0, 101.0, 102.0, 103.0, 104.0, 100.0])
    store = make_store(rows)
    ind = SessionHighLowPct(store, "TEST", "15min")
    result = await ind.compute(SessionHighLowPct.Parameters(session_open_utc=_SESSION_OPEN))
    assert result is not None
    assert 0.0 <= result <= 1.0
