# quantindicators

Polars-based technical indicator library for OHLCV data. Used by [trading-platform](https://github.com/SakethThogarucheeti/trading-platform) as a local editable dependency.

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
import polars as pl
from quantindicators import PolarsIndicatorStore

store = PolarsIndicatorStore()

# df is a Polars DataFrame with columns: open, high, low, close, volume, timestamp
store.update(df)

ema = store.ema(period=9)        # pl.Series
rsi = store.rsi(period=14)       # pl.Series
atr = store.atr(period=14)       # pl.Series
vwap = store.vwap()              # pl.Series
```

Each indicator call returns a `pl.Series` aligned to the input DataFrame rows.

## Testing

```bash
uv run pytest
```

## Used by

[trading-platform](https://github.com/SakethThogarucheeti/trading-platform) installs this as an editable dependency via:

```toml
[tool.uv.sources]
quantindicators = { path = "../quantindicators", editable = true }
```

Clone both repos into the same parent directory for this to resolve correctly.
