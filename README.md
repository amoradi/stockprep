# stockprep

Source-agnostic stock data prep utilities. Bring your own data fetcher.

## Why?

Stock data comes from many sources (Yahoo Finance, Alpaca, CSVs, etc.), but the prep steps are always the same:

1. Fetch price data
2. Handle missing values (forward/backward fill)
3. Normalize for comparison (start all at 1.0)
4. Calculate returns

This package decouples the **data source** from the **prep logic**. You define how to fetch, it handles the rest.

## Usage

```python
from stock_data import StockData

# Define your fetcher - any function that returns a DataFrame
# with DatetimeIndex and symbols as columns
def my_fetcher(symbols, start, end):
    import yfinance as yf
    df = yf.download(symbols, start=start, end=end, progress=False)["Adj Close"]
    return df if len(symbols) > 1 else df.to_frame(symbols[0])

# Use it
data = StockData(my_fetcher)
data.load(["AAPL", "GOOG", "SPY"], "2020-01-01", "2023-12-31")

# Normalized prices (all start at 1.0)
data.normalize()

# Daily returns
data.daily_returns()

# Cumulative returns
data.cumulative_returns()

# Access raw/cleaned data
data.raw      # before cleaning
data.prices   # after ffill/bfill
```

## Fetcher Contract

A fetcher is any callable with this signature:

```python
def fetcher(symbols: list, start: str, end: str) -> pd.DataFrame:
    """
    Returns DataFrame with:
    - DatetimeIndex (dates)
    - Columns = symbol names
    - Values = prices (typically Adj Close)
    """
    pass
```

## Example Fetchers

See `fetchers.py` for ready-to-use examples:

- `yfinance_fetcher` - Yahoo Finance
- `csv_fetcher(data_dir)` - Local CSV files
- `alpaca_fetcher(api_key, secret)` - Alpaca Markets API

```python
from fetchers import yfinance_fetcher, csv_fetcher

# Yahoo Finance
data = StockData(yfinance_fetcher)

# Local CSVs
data = StockData(csv_fetcher("./my_data"))
```

## Install

Just copy `stock_data.py` into your project. That's it.

For fetchers, install what you need:
```bash
pip install yfinance      # for yfinance_fetcher
pip install alpaca-py     # for alpaca_fetcher
```

## License

MIT
