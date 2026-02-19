"""
Example fetcher functions for common data sources.

These are examples - copy and modify for your own use.
"""

import pandas as pd


def yfinance_fetcher(symbols: list, start: str, end: str) -> pd.DataFrame:
    """
    Fetch from Yahoo Finance using yfinance.

    pip install yfinance
    """
    import yfinance as yf

    df = yf.download(symbols, start=start, end=end, progress=False)["Adj Close"]

    # Single symbol returns Series, convert to DataFrame
    if isinstance(df, pd.Series):
        df = df.to_frame(symbols[0])

    return df


def csv_fetcher(data_dir: str = "data"):
    """
    Factory that returns a fetcher for local CSV files.

    Expects files like: data/AAPL.csv with 'Date' and 'Adj Close' columns.

    Usage:
        fetcher = csv_fetcher("./my_data")
        data = StockData(fetcher)
    """
    def fetch(symbols: list, start: str, end: str) -> pd.DataFrame:
        dates = pd.date_range(start, end)
        df = pd.DataFrame(index=dates)

        for symbol in symbols:
            path = f"{data_dir}/{symbol}.csv"
            temp = pd.read_csv(
                path,
                index_col="Date",
                parse_dates=True,
                usecols=["Date", "Adj Close"],
                na_values=["nan"],
            )
            temp = temp.rename(columns={"Adj Close": symbol})
            df = df.join(temp)

        return df.dropna(how="all")

    return fetch


def alpaca_fetcher(api_key: str, secret_key: str):
    """
    Factory that returns a fetcher for Alpaca Markets API.

    pip install alpaca-py

    Usage:
        fetcher = alpaca_fetcher("your_key", "your_secret")
        data = StockData(fetcher)
    """
    def fetch(symbols: list, start: str, end: str) -> pd.DataFrame:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
        from datetime import datetime

        client = StockHistoricalDataClient(api_key, secret_key)

        request = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=TimeFrame.Day,
            start=datetime.fromisoformat(start),
            end=datetime.fromisoformat(end),
        )

        bars = client.get_stock_bars(request).df

        # Pivot to get symbols as columns
        df = bars["close"].unstack(level="symbol")

        return df

    return fetch
