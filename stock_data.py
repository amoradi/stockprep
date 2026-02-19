"""
stockprep - Source-agnostic stock data preparation utilities.

Bring your own fetcher, get normalized/cleaned price data.
"""

import pandas as pd
from typing import Callable, Protocol


class DataProvider(Protocol):
    """Any callable that takes (symbols, start, end) -> DataFrame"""
    def __call__(self, symbols: list, start: str, end: str) -> pd.DataFrame: ...


FetchFn = Callable[[list, str, str], pd.DataFrame]


class StockData:
    """
    Source-agnostic stock data container with common prep operations.

    Usage:
        def my_fetcher(symbols, start, end):
            # return DataFrame with DatetimeIndex, columns = symbols
            ...

        data = StockData(my_fetcher)
        data.load(["AAPL", "GOOG"], "2020-01-01", "2023-01-01")

        normalized = data.normalize()
        returns = data.daily_returns()
    """

    def __init__(self, fetch: FetchFn):
        self.fetch = fetch
        self.raw: pd.DataFrame | None = None
        self.prices: pd.DataFrame | None = None

    def load(self, symbols: list, start: str, end: str) -> "StockData":
        """Fetch and clean price data."""
        self.raw = self.fetch(symbols, start, end)
        self.prices = self._clean(self.raw)
        return self

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Forward fill then backward fill missing values."""
        return df.ffill().bfill()

    def normalize(self) -> pd.DataFrame:
        """Normalize prices so all start at 1.0."""
        if self.prices is None:
            raise ValueError("No data loaded. Call load() first.")
        return self.prices / self.prices.iloc[0]

    def daily_returns(self) -> pd.DataFrame:
        """Calculate daily percentage returns."""
        if self.prices is None:
            raise ValueError("No data loaded. Call load() first.")
        return self.prices.pct_change().iloc[1:]

    def cumulative_returns(self) -> pd.DataFrame:
        """Calculate cumulative returns from start."""
        if self.prices is None:
            raise ValueError("No data loaded. Call load() first.")
        return (self.prices / self.prices.iloc[0]) - 1
