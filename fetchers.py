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


def nasdaqdatalink_fetcher(api_key: str):
    """
    Factory that returns a fetcher for Nasdaq Data Link (Sharadar).

    SURVIVORSHIP BIAS FREE - includes delisted stocks.

    pip install nasdaq-data-link

    Requires Sharadar subscription (~$50/mo for SEP table).

    Usage:
        fetcher = nasdaqdatalink_fetcher("your_api_key")
        data = StockData(fetcher)
    """
    def fetch(symbols: list, start: str, end: str) -> pd.DataFrame:
        import nasdaqdatalink

        nasdaqdatalink.ApiConfig.api_key = api_key

        # Sharadar SEP table has daily prices including delisted stocks
        df = nasdaqdatalink.get_table(
            "SHARADAR/SEP",
            ticker=symbols,
            date={"gte": start, "lte": end},
            paginate=True,
        )

        # Pivot to standard format
        df = df.pivot(index="date", columns="ticker", values="closeadj")
        df.index = pd.to_datetime(df.index)

        return df

    return fetch


def tiingo_fetcher(api_key: str):
    """
    Factory that returns a fetcher for Tiingo.

    SURVIVORSHIP BIAS FREE - includes delisted stocks.

    pip install requests

    Free tier available at tiingo.com

    Usage:
        fetcher = tiingo_fetcher("your_api_key")
        data = StockData(fetcher)
    """
    def fetch(symbols: list, start: str, end: str) -> pd.DataFrame:
        import requests

        frames = []
        for symbol in symbols:
            url = f"https://api.tiingo.com/tiingo/daily/{symbol}/prices"
            params = {
                "startDate": start,
                "endDate": end,
                "token": api_key,
            }
            resp = requests.get(url, params=params)
            resp.raise_for_status()

            data = resp.json()
            if data:
                df = pd.DataFrame(data)
                df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
                df = df.set_index("date")[["adjClose"]]
                df = df.rename(columns={"adjClose": symbol})
                frames.append(df)

        return pd.concat(frames, axis=1) if frames else pd.DataFrame()

    return fetch