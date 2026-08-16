# quantindicators

Polars-based technical indicator library for OHLCV data. Streaming/incremental: each indicator is constructed against a candle store and computes its current value per call, for use inside a live strategy loop (as opposed to a batch/vectorized pass over full history). Used by [trading-strategy-sdk](https://github.com/SakethThogarucheeti/trading-strategy-sdk) and [trading-platform](https://github.com/SakethThogarucheeti/trading-platform) as a git dependency.

## Indicators

| Category | Indicators |
|----------|-----------|
| Trend | EMA, SMA, MACD, ADX, Aroon, Supertrend, Parabolic SAR, Chandelier Exit |
| Momentum | RSI, Stochastic, Stochastic RSI, Connors RSI, Williams %R, CCI, TSI, ROC, Momentum, Coppock Curve, DPO |
| Volatility | ATR, Normalized ATR, Bollinger Bands, Keltner Channel, Historical Volatility, Chaikin Volatility, Squeeze Momentum |
| Volume | VWAP, VWAP Bands, VWMA, OBV, MFI, CMF, PVT, RVOL, VROC |
| Price | Pivot Points, Donchian Channel, Opening Range, Distance from MA, Price Percentile, Price vs 52W High, Session High/Low %, Fisher Transform, Elder Ray, Linear Regression Slope, Mean Reversion Score |
| Candle | Inside Bar, Candle Body Ratio, Upper Shadow Ratio, Gap, True Range |

## Stack

- Python 3.13+, [uv](https://docs.astral.sh/uv/)
- NumPy, Pydantic
- SciPy (optional, for RSI divergence and Stochastic variants)

## Setup

```bash
uv sync
```

For SciPy-dependent indicators:

```bash
uv sync --extra scipy
```

## Usage

```python
from quantindicators import EMA, ATR, RSI
from quantindicators.polars_store import PolarsStore

store = PolarsStore()
store.push("RELIANCE", "15min", candle_row)

ema = EMA(store, "RELIANCE", "15min")
value = await ema.compute(EMA.Parameters(period=9))
```

Indicators are constructed with runtime dependencies (store, symbol, interval) and called with configuration parameters per `compute()` call — each call returns the indicator's current value from the store's most recent candles, not a full historical series.

## Testing

```bash
uv run pytest
```

## Used by

[trading-strategy-sdk](https://github.com/SakethThogarucheeti/trading-strategy-sdk) and [trading-platform](https://github.com/SakethThogarucheeti/trading-platform) install this as a git dependency:

```toml
[tool.uv.sources]
quantindicators = { git = "https://github.com/SakethThogarucheeti/quantindicators.git" }
```

No local checkout or shared parent directory required — this is a standalone, independently installable package, same pattern as `trading-types`, `trading-strategy-sdk`, and `trading-risk-sdk`.
