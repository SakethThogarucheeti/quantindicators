"""Tests for quantindicators/base.py — registry and alias guard."""

from __future__ import annotations

import pytest

from quantindicators.base import Indicator


def test_indicator_aliases_registered() -> None:
    import quantindicators  # noqa: F401
    from quantindicators.base import _REGISTRY

    for alias in (
        "ema",
        "sma",
        "rsi",
        "atr",
        "vwap",
        "wilder_ema",
        "true_range",
        "macd",
        "bollinger",
        "stochastic",
        "cci",
        "williams_r",
        "roc",
        "momentum",
        "donchian",
        "keltner",
        "hv",
        "obv",
        "mfi",
        "cmf",
        "vwma",
        "pivot",
        "supertrend",
        "psar",
        "adx",
        "chaikin_vol",
        "aroon",
        "candle_body_ratio",
        "chandelier_exit",
        "connors_rsi",
        "coppock_curve",
        "distance_from_ma",
        "donchian",
        "dpo",
        "elder_ray",
        "fisher_transform",
        "gap",
        "inside_bar",
        "linreg_slope",
        "mean_reversion_score",
        "momentum",
        "normalized_atr",
        "opening_range",
        "price_percentile",
        "price_vs_52w_high",
        "pvt",
        "rsi_divergence",
        "rvol",
        "session_hl_pct",
        "squeeze_momentum",
        "stochastic_rsi",
        "tsi",
        "ultimate_oscillator",
        "upper_shadow_ratio",
        "volatility_ratio",
        "vroc",
        "vwap_bands",
        "weekly_rsi",
    ):
        assert alias in _REGISTRY, f"alias {alias!r} not registered"


def test_duplicate_alias_raises() -> None:
    with pytest.raises(ValueError, match="Duplicate Indicator alias"):

        class _DupEMA(Indicator):
            alias = "ema"

            async def compute(self, params): ...  # type: ignore[override]


def test_missing_alias_is_allowed_for_abstract_intermediates() -> None:
    class _AbstractMid(Indicator):
        async def compute(self, params): ...  # type: ignore[override]

    # No alias → no registration, no error
    from quantindicators.base import _REGISTRY

    assert _AbstractMid not in _REGISTRY.values()


def test_empty_alias_raises() -> None:
    with pytest.raises(TypeError, match="alias must be a non-empty string"):

        class _Bad(Indicator):
            alias = ""

            async def compute(self, params): ...  # type: ignore[override]


def test_lookup_raises_for_unknown_alias() -> None:
    import quantindicators  # noqa: F401 — ensure registry is populated

    with pytest.raises(ValueError, match="Unknown Indicator alias"):
        Indicator.lookup("this_does_not_exist_xyz")


def test_registered_returns_dict_with_known_aliases() -> None:
    import quantindicators  # noqa: F401

    reg = Indicator.registered()
    assert isinstance(reg, dict)
    assert "ema" in reg
    assert "rsi" in reg


@pytest.mark.parametrize(
    "module_path,class_name",
    [
        ("quantindicators.library.adx", "ADX"),
        ("quantindicators.library.aroon", "Aroon"),
        ("quantindicators.library.atr", "ATR"),
        ("quantindicators.library.bollinger", "BollingerBands"),
        ("quantindicators.library.candle_body_ratio", "CandleBodyRatio"),
        ("quantindicators.library.cci", "CCI"),
        ("quantindicators.library.chaikin_volatility", "ChaikinVolatility"),
        ("quantindicators.library.chandelier_exit", "ChandelierExit"),
        ("quantindicators.library.cmf", "CMF"),
        ("quantindicators.library.connors_rsi", "ConnorsRSI"),
        ("quantindicators.library.coppock_curve", "CoppockCurve"),
        ("quantindicators.library.distance_from_ma", "DistanceFromMA"),
        ("quantindicators.library.donchian", "DonchianChannels"),
        ("quantindicators.library.dpo", "DPO"),
        ("quantindicators.library.elder_ray", "ElderRay"),
        ("quantindicators.library.ema", "EMA"),
        ("quantindicators.library.fisher_transform", "FisherTransform"),
        ("quantindicators.library.gap", "GapSize"),
        ("quantindicators.library.historical_volatility", "HistoricalVolatility"),
        ("quantindicators.library.inside_bar", "InsideBar"),
        ("quantindicators.library.keltner", "KeltnerChannels"),
        ("quantindicators.library.linreg_slope", "LinearRegressionSlope"),
        ("quantindicators.library.macd", "MACD"),
        ("quantindicators.library.mean_reversion_score", "MeanReversionScore"),
        ("quantindicators.library.mfi", "MFI"),
        ("quantindicators.library.momentum", "Momentum"),
        ("quantindicators.library.normalized_atr", "NormalizedATR"),
        ("quantindicators.library.obv", "OBV"),
        ("quantindicators.library.opening_range", "OpeningRangePosition"),
        ("quantindicators.library.parabolic_sar", "ParabolicSAR"),
        ("quantindicators.library.pivot", "PivotPoints"),
        ("quantindicators.library.price_percentile", "PricePercentile"),
        ("quantindicators.library.price_vs_52w_high", "PriceVs52wHigh"),
        ("quantindicators.library.pvt", "PVT"),
        ("quantindicators.library.roc", "ROC"),
        ("quantindicators.library.rsi", "RSI"),
        ("quantindicators.library.rsi_divergence", "RSIDivergence"),
        ("quantindicators.library.rvol", "RVOL"),
        ("quantindicators.library.session_high_low_pct", "SessionHighLowPct"),
        ("quantindicators.library.sma", "SMA"),
        ("quantindicators.library.squeeze_momentum", "SqueezeMomentum"),
        ("quantindicators.library.stochastic", "Stochastic"),
        ("quantindicators.library.stochastic_rsi", "StochasticRSI"),
        ("quantindicators.library.supertrend", "Supertrend"),
        ("quantindicators.library.true_range", "TrueRange"),
        ("quantindicators.library.tsi", "TSI"),
        ("quantindicators.library.ultimate_oscillator", "UltimateOscillator"),
        ("quantindicators.library.upper_shadow_ratio", "UpperShadowRatio"),
        ("quantindicators.library.volatility_ratio", "VolatilityRatio"),
        ("quantindicators.library.vroc", "VROC"),
        ("quantindicators.library.vwap", "VWAP"),
        ("quantindicators.library.vwap_bands", "VWAPBands"),
        ("quantindicators.library.vwma", "VWMA"),
        ("quantindicators.library.weekly_rsi", "WeeklyRSI"),
        ("quantindicators.library.wilder_ema", "WilderEMA"),
        ("quantindicators.library.williams_r", "WilliamsR"),
    ],
)
def test_indicator_repr(module_path: str, class_name: str) -> None:
    """All indicators implement __repr__ — call it to hit the return line."""
    import importlib
    from unittest.mock import AsyncMock, MagicMock

    from quantindicators.store import AbstractCandleStore

    mod = importlib.import_module(module_path)
    cls = getattr(mod, class_name)
    store = MagicMock(spec=AbstractCandleStore)
    store.fetch = AsyncMock(return_value=[])
    store.fetch_since = AsyncMock(return_value=[])
    ind = cls(store, "TEST", "15min")
    result = repr(ind)
    assert isinstance(result, str)
    assert len(result) > 0
