import pandas as pd
import time

from collections.abc import Callable
from massive import RESTClient
from massive.rest.models import FuturesContract, FuturesProduct, TickerDetails
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Seconds to wait after each API request
REQUEST_DELAY = 12


def polygon_fetch_ticker_details(
    ticker: str,
    client: RESTClient | None = None,
) -> TickerDetails:
    """
    Fetch detailed information for a given product from Polygon API.

    Parameters:
    -----------
    ticker : str
        Ticker symbol to download.
    client : RESTClient, optional
        Client to use for the request. If None, a new client is created using
        the POLYGON_KEY setting.

    Returns:
    --------
    details : TickerDetails
        Object containing detailed information about the ticker (for example,
        the name field).
    """

    if client is None:
        client = RESTClient(api_key=config("POLYGON_KEY"))

    details = client.get_ticker_details(ticker)

    return details


def polygon_fetch_futures_contract_details(
    ticker: str,
    client: RESTClient | None = None,
) -> FuturesContract:
    """
    Fetch the most recent record for a futures contract from the Polygon
    futures contracts endpoint.

    Parameters:
    -----------
    ticker : str
        Futures contract ticker (for example, ESZ6).
    client : RESTClient, optional
        Client to use for the request. If None, a new client is created using
        the POLYGON_KEY setting.

    Returns:
    --------
    contract : FuturesContract
        Object containing details about the contract (for example, the
        product_code and last_trade_date fields).

    Raises:
    -------
    LookupError
        If no contract is found for the ticker.
    """

    if client is None:
        client = RESTClient(api_key=config("POLYGON_KEY"))

    contracts = client.list_futures_contracts(ticker=ticker, sort="date.desc", limit=1)
    contract = next(iter(contracts), None)

    if contract is None:
        raise LookupError(f"No futures contract found for {ticker}")

    return contract


def polygon_fetch_futures_product_details(
    product_code: str,
    client: RESTClient | None = None,
) -> FuturesProduct | None:
    """
    Fetch the most recent record for a futures product from the Polygon
    futures products endpoint.

    Parameters:
    -----------
    product_code : str
        Futures product code (for example, ES).
    client : RESTClient, optional
        Client to use for the request. If None, a new client is created using
        the POLYGON_KEY setting.

    Returns:
    --------
    product : FuturesProduct or None
        Object containing details about the product (for example, the name
        field), or None if no product is found.
    """

    if client is None:
        client = RESTClient(api_key=config("POLYGON_KEY"))

    products = client.list_futures_products(
        product_code=product_code, sort="date.desc", limit=1
    )

    return next(iter(products), None)


def fetch_ticker_name(
    ticker: str,
    client: RESTClient,
) -> str:
    """
    Return the name of an equity, ETF, option underlying, or index ticker.
    """

    return polygon_fetch_ticker_details(ticker, client=client).name


def fetch_futures_name(
    ticker: str,
    client: RESTClient,
) -> str:
    """
    Return the name of a futures contract's product (for example, ESZ6 returns
    the name of the ES product). Falls back to the contract's own name if the
    product has none. Makes two API requests, with a pause between them.
    """

    contract = polygon_fetch_futures_contract_details(ticker, client=client)
    time.sleep(REQUEST_DELAY)
    product = polygon_fetch_futures_product_details(
        contract.product_code, client=client
    )

    if product is not None and product.name:
        return product.name

    return contract.name


def update_ticker_names(
    tickers: list[str],
    csv_name: str,
    client: RESTClient,
    fetch_name: Callable[[str, RESTClient], str] = fetch_ticker_name,
) -> None:
    """
    Fetch the names of new tickers and add them to a csv file. The file is saved
    after each ticker, so a failed request keeps the names fetched before it. If
    there are no new tickers, nothing is read or written.

    Parameters:
    -----------
    tickers : list[str]
        Ticker symbols to fetch names for.
    csv_name : str
        Name of the csv file in DATA_DIR/Polygon to update.
    client : RESTClient
        Client to use for the requests.
    fetch_name : Callable[[str, RESTClient], str], optional
        Function that returns the name for a ticker. Defaults to
        fetch_ticker_name; use fetch_futures_name for futures contracts.

    Returns:
    --------
    None
    """

    if not tickers:
        return

    csv_path = f"{DATA_DIR}/Polygon/{csv_name}"

    # Read existing data from csv file into names dictionary
    try:
        names = pd.read_csv(csv_path, index_col=0).to_dict()["Name"]
    except FileNotFoundError:
        names = {}

    for ticker in tickers:
        names[ticker] = fetch_name(ticker, client)
        names = dict(sorted(names.items()))

        # Export names dictionary to csv file
        names_df = pd.DataFrame.from_dict(names, orient="index", columns=["Name"])
        names_df.to_csv(csv_path)

        print(f"Updated {ticker}")
        time.sleep(REQUEST_DELAY)

    print(names)


if __name__ == "__main__":

    new_tickers = {
        "equities.csv": [
            # Put new tickers here that you want to pull details for
            "SPCX",
        ],
        "etfs.csv": [
            # Put new tickers here that you want to pull details for
            "JETS",
        ],
        "options.csv": [
            # Put new tickers here that you want to pull details for
            "QQQ",
        ],
        "indices.csv": [
            # Put new tickers here that you want to pull details for
            "I:NDX",
        ],
        "futures.csv": [
            # Put new tickers here that you want to pull details for
            "ESZ6",
        ],
    }

    # Open client connection
    client = RESTClient(api_key=config("POLYGON_KEY"))

    for csv_name, tickers in new_tickers.items():
        # Futures use the futures endpoints instead of the ticker details endpoint
        if csv_name == "futures.csv":
            fetch_name = fetch_futures_name
        else:
            fetch_name = fetch_ticker_name

        update_ticker_names(tickers, csv_name, client, fetch_name)
