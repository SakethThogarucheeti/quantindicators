"""
quantindicators — async technical indicator library for OHLCV data.

Indicators are constructed with runtime dependencies (store, symbol, interval)
and called with configuration parameters per compute() call.

Usage::

    from quantindicators import EMA, ATR, RSI
    from quantindicators.polars_store import PolarsStore

Example::

    store = PolarsStore()
    store.push("RELIANCE", "15min", candle_row)

    ema = EMA(store, "RELIANCE", "15min")
    value = await ema.compute(EMA.Parameters(period=9))
"""

from quantindicators.base import Indicator, IndicatorParameters
from quantindicators.library.adx import ADX
from quantindicators.library.aroon import Aroon
from quantindicators.library.atr import ATR
from quantindicators.library.bollinger import BollingerBands
from quantindicators.library.candle_body_ratio import CandleBodyRatio
from quantindicators.library.cci import CCI
from quantindicators.library.chaikin_volatility import ChaikinVolatility
from quantindicators.library.chandelier_exit import ChandelierExit
from quantindicators.library.cmf import CMF
from quantindicators.library.connors_rsi import ConnorsRSI
from quantindicators.library.coppock_curve import CoppockCurve
from quantindicators.library.distance_from_ma import DistanceFromMA
from quantindicators.library.donchian import DonchianChannels
from quantindicators.library.dpo import DPO
from quantindicators.library.elder_ray import ElderRay
from quantindicators.library.ema import EMA
from quantindicators.library.fisher_transform import FisherTransform
from quantindicators.library.gap import GapSize
from quantindicators.library.historical_volatility import HistoricalVolatility
from quantindicators.library.inside_bar import InsideBar
from quantindicators.library.keltner import KeltnerChannels
from quantindicators.library.linreg_slope import LinearRegressionSlope
from quantindicators.library.macd import MACD
from quantindicators.library.mean_reversion_score import MeanReversionScore
from quantindicators.library.mfi import MFI
from quantindicators.library.momentum import Momentum
from quantindicators.library.normalized_atr import NormalizedATR
from quantindicators.library.obv import OBV
from quantindicators.library.opening_range import OpeningRangePosition
from quantindicators.library.parabolic_sar import ParabolicSAR
from quantindicators.library.pivot import PivotPoints
from quantindicators.library.price_percentile import PricePercentile
from quantindicators.library.price_vs_52w_high import PriceVs52wHigh
from quantindicators.library.pvt import PVT
from quantindicators.library.roc import ROC
from quantindicators.library.rsi import RSI
from quantindicators.library.rsi_divergence import RSIDivergence
from quantindicators.library.rvol import RVOL
from quantindicators.library.session_high_low_pct import SessionHighLowPct
from quantindicators.library.sma import SMA
from quantindicators.library.squeeze_momentum import SqueezeMomentum
from quantindicators.library.stochastic import Stochastic
from quantindicators.library.stochastic_rsi import StochasticRSI
from quantindicators.library.supertrend import Supertrend
from quantindicators.library.true_range import TrueRange
from quantindicators.library.tsi import TSI
from quantindicators.library.ultimate_oscillator import UltimateOscillator
from quantindicators.library.upper_shadow_ratio import UpperShadowRatio
from quantindicators.library.volatility_ratio import VolatilityRatio
from quantindicators.library.vroc import VROC
from quantindicators.library.vwap import VWAP
from quantindicators.library.vwap_bands import VWAPBands
from quantindicators.library.vwma import VWMA
from quantindicators.library.weekly_rsi import WeeklyRSI
from quantindicators.library.wilder_ema import WilderEMA
from quantindicators.library.williams_r import WilliamsR
from quantindicators.polars_store import PolarsStore
from quantindicators.store import AbstractCandleStore

__all__ = [
    # Base
    "Indicator",
    "IndicatorParameters",
    "AbstractCandleStore",
    "PolarsStore",
    # Moving averages
    "EMA",
    "SMA",
    "VWMA",
    "WilderEMA",
    # Momentum / oscillators
    "RSI",
    "MACD",
    "Stochastic",
    "StochasticRSI",
    "CCI",
    "WilliamsR",
    "ROC",
    "Momentum",
    "TSI",
    "UltimateOscillator",
    "FisherTransform",
    "ConnorsRSI",
    # Volatility / channels
    "ATR",
    "NormalizedATR",
    "BollingerBands",
    "KeltnerChannels",
    "DonchianChannels",
    "HistoricalVolatility",
    "ChaikinVolatility",
    "VolatilityRatio",
    # Trend / direction
    "ADX",
    "Aroon",
    "Supertrend",
    "ParabolicSAR",
    "CoppockCurve",
    "DPO",
    "ChandelierExit",
    "ElderRay",
    # Volume
    "OBV",
    "MFI",
    "CMF",
    "VWAP",
    "VWAPBands",
    "RVOL",
    "VROC",
    "PVT",
    # Composite / advanced
    "SqueezeMomentum",
    "MeanReversionScore",
    "RSIDivergence",
    "WeeklyRSI",
    "LinearRegressionSlope",
    # Candle / session
    "CandleBodyRatio",
    "InsideBar",
    "OpeningRangePosition",
    "SessionHighLowPct",
    "UpperShadowRatio",
    "GapSize",
    # Price structure
    "TrueRange",
    "PivotPoints",
    "PricePercentile",
    "PriceVs52wHigh",
    "DistanceFromMA",
]
