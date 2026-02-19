"""
Example usage of stockprep.
"""

import sys
sys.path.insert(0, "..")

from stock_data import StockData
from fetchers import yfinance_fetcher


def main():
    # Initialize with your fetcher of choice
    data = StockData(yfinance_fetcher)

    # Load some stocks
    data.load(["AAPL", "GOOG", "SPY"], "2020-01-01", "2023-12-31")

    # Get normalized prices (all start at 1.0)
    normalized = data.normalize()
    print("Normalized prices (first 5 rows):")
    print(normalized.head())
    print()

    # Get daily returns
    returns = data.daily_returns()
    print("Daily returns (first 5 rows):")
    print(returns.head())
    print()

    # Get cumulative returns
    cumulative = data.cumulative_returns()
    print("Cumulative returns (last 5 rows):")
    print(cumulative.tail())

    # Plot comparison
    normalized.plot(title="Normalized Price Comparison", figsize=(12, 6))


if __name__ == "__main__":
    main()
