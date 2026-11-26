import os
import requests
import time

from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Each index has one CSV holding its full daily history, refreshed daily. These
# are the links on https://www.cboe.com/tradable-products/vix/vix-historical-data/
CBOE_INDEX_URL = (
    "https://cdn-api.cboe.com/api/global/us_indices/daily_prices/{symbol}_History.csv"
)

# Cboe returns 403 / 404 pages for requests without a browser-like user agent
HEADERS = {"User-Agent": "Mozilla/5.0"}

# First bytes of a valid index CSV, used to reject error pages saved as CSV. The
# header is either "DATE,OPEN,HIGH,LOW,CLOSE" or "DATE,<SYMBOL>"
CSV_HEADER = b"DATE,"


def cboe_pull_index_data(
    base_directory,
    symbols: list[str],
    source: str = "Cboe",
    asset_class: str = "Indices",
    timespan: str = "day",
    pause: float = 0.5,
    verbose: bool = True,
) -> list[str]:
    """
    Download the daily history CSV for each Cboe index.

    Each file holds the index's full history and changes daily, so every file
    is downloaded again on every run. Any failure raises immediately; files
    already saved are kept.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    symbols : list[str]
        Cboe index symbols (e.g., "VIX", "VIX3M", "VVIX").
    source : str
        Name of the data source (e.g., "Cboe").
    asset_class : str
        Asset class name (e.g., "Indices").
    timespan : str
        Time span of the data (e.g., "day").
    pause : float
        Seconds to sleep between downloads.
    verbose : bool
        If True, print a line for each index.

    Returns:
    --------
    downloaded : list[str]
        File names of the saved CSVs.
    """

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    os.makedirs(directory, exist_ok=True)

    downloaded = []

    for symbol in symbols:
        file_name = f"{symbol}_History.csv"
        file_location = f"{directory}/{file_name}"
        url = CBOE_INDEX_URL.format(symbol=symbol)

        try:
            # An unknown symbol returns a 403 with an XML error body
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()

            if not response.content.startswith(CSV_HEADER):
                raise ValueError(
                    f"Response does not start with the expected CSV header {CSV_HEADER!r}."
                )

            # Write to a temporary file and then move it into place, so that a
            # failed write never leaves a partial file behind
            temp_location = f"{file_location}.tmp"
            with open(temp_location, "wb") as f:
                f.write(response.content)
            os.replace(temp_location, file_location)

        except Exception as e:
            print(f"Failed to download Cboe index {symbol} from {url}: {e}")
            raise

        downloaded.append(file_name)
        if verbose == True:
            last_line = response.content.rstrip().splitlines()[-1].decode()
            last_date = last_line.split(",")[0]
            print(f"Downloaded {symbol} ({file_name}), last date {last_date}.")

        time.sleep(pause)

    print(
        f"Cboe index data complete: {len(downloaded)} downloaded, saved to {directory}."
    )
    print(f"--------------------")

    return downloaded


if __name__ == "__main__":

    # Cboe indices to pull
    symbols = [
        "VIX",
        "VIX1D",
        "VIX9D",
        "VIX3M",
        "VIX6M",
        "VIX1Y",
        "VVIX",
        "SKEW",
        "VXN",
        "VXD",
        "RVX",
        "GVZ",
        "OVX",
        "VXTLT",
        "VXEEM",
        "VXAPL",
        "VXAZN",
    ]

    cboe_pull_index_data(
        base_directory=DATA_DIR,
        symbols=symbols,
        source="Cboe",
        asset_class="Indices",
        timespan="day",
        pause=0.5,
        verbose=True,
    )
