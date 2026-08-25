"""Indicator abstract base class and plugin registry."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import numpy as np
from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from datetime import datetime

    from quantindicators.store import AbstractCandleStore

_log = logging.getLogger(__name__)

_REGISTRY: dict[str, type[Indicator]] = {}


class IndicatorParameters(BaseModel):
    """Frozen Pydantic base for all indicator parameter sets."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Indicator(ABC):
    """
    Abstract base for a single technical indicator.

    Subclasses set a class-level ``alias`` to auto-register. Construction takes
    runtime dependencies only (store, symbol, interval, and optionally a
    session_open_utc datetime for session-aware indicators). Configuration
    parameters are passed per call via ``compute(params)`` — making each compute
    call stateless and allowing the same instance to be reused across parameter sweeps.

    Each subclass must define a nested ``Parameters(IndicatorParameters)`` class
    and implement ``compute(params)``.
    """

    alias: str  # set on concrete subclasses to register

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        alias = cls.__dict__.get("alias")
        if alias is None:
            return
        if not isinstance(alias, str) or not alias:
            raise TypeError(f"{cls.__name__}.alias must be a non-empty string")
        if alias in _REGISTRY and _REGISTRY[alias] is not cls:
            raise ValueError(
                f"Duplicate Indicator alias {alias!r}: already registered by "
                f"{_REGISTRY[alias].__qualname__}, cannot also register {cls.__qualname__}."
            )
        _REGISTRY[alias] = cls

    def __init__(self, store: AbstractCandleStore, symbol: str, interval: str) -> None:
        self._store = store
        self._symbol = symbol
        self._interval = interval

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    @abstractmethod
    async def compute(self, params: Any) -> float | None:
        """
        Fetch candles and return the current indicator value.

        Returns None when there are fewer bars than required (warmup not done).
        Implementations must call ``self._store.fetch(...)`` for data.
        Configuration (period, multiplier, etc.) comes from ``params``.

        Typed as ``Any`` rather than ``IndicatorParameters`` deliberately: every
        subclass narrows this to its own nested ``Parameters`` type (e.g.
        ``async def compute(self, params: RSI.Parameters)``), which a stricter
        base signature would reject as a Liskov violation on every override.
        Nothing dispatches on this method polymorphically through the base
        type — every real call site already knows the concrete subclass
        statically (``RSI(...).compute(RSI.Parameters(...))``), except
        ``Indicator.lookup(alias)`` below, which is a Factory Method boundary
        where type erasure is correct, not a defect. ``Any`` here lets each
        override keep its own precisely-checked parameter type instead of
        every subclass needing a ``# type: ignore[override]``.
        """

    # ------------------------------------------------------------------
    # Shared fetch-and-extract helpers for compute() implementations
    # ------------------------------------------------------------------

    async def _fetch_columns(
        self, fetch_n: int, *cols: str, min_len: int | None = None
    ) -> dict[str, np.ndarray] | None:
        """
        Fetch the last ``fetch_n`` candles and extract ``cols`` as numpy arrays.

        Returns None (warmup not done) when fewer than ``min_len`` rows come
        back — ``min_len`` defaults to ``fetch_n`` but can be set lower for
        indicators whose guard threshold differs from how many bars they
        request (e.g. fetching extra lookback bars for a rolling computation).
        """
        rows = await self._store.fetch(self._symbol, self._interval, fetch_n)
        if len(rows) < (min_len if min_len is not None else fetch_n):
            return None
        return {c: np.array([r[c] for r in rows], dtype=float) for c in cols}

    async def _fetch_columns_since(
        self, since: datetime, *cols: str, min_len: int = 2
    ) -> dict[str, np.ndarray] | None:
        """Session-anchored counterpart of ``_fetch_columns``, via ``fetch_since``."""
        rows = await self._store.fetch_since(self._symbol, self._interval, since)
        if len(rows) < min_len:
            return None
        return {c: np.array([r[c] for r in rows], dtype=float) for c in cols}

    # ------------------------------------------------------------------
    # Registry helpers
    # ------------------------------------------------------------------

    @classmethod
    def lookup(cls, alias: str) -> type[Indicator]:
        try:
            return _REGISTRY[alias]
        except KeyError:
            available = ", ".join(sorted(_REGISTRY))
            raise ValueError(
                f"Unknown Indicator alias {alias!r}. Available: {available or '(none)'}."
            ) from None

    @classmethod
    def registered(cls) -> dict[str, type[Indicator]]:
        return dict(_REGISTRY)
