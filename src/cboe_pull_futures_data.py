import os
import re
import requests
import time

from datetime import date
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Cboe endpoints. The product list is the JSON endpoint called by the Cboe
# historical data page, and each contract's "path" is relative to the CDN root.
CBOE_PRODUCT_LIST_URL = (
    "https://www-api.cboe.com/us/futures/market_statistics/historical_data/"
    "product/list/{root}/"
)
CBOE_CDN_URL = "https://cdn.cboe.com/"

# Cboe returns 403 / 404 pages for requests without a browser-like user agent
HEADERS = {"User-Agent": "Mozilla/5.0"}

# First bytes of a valid contract CSV, used to reject error pages saved as CSV
CSV_HEADER = b"Trade Date"

# Pre-2013 archive. The page builds its download links client side from a
# contract list embedded in one of its Next.js JavaScript chunks, so the list is
# read from that chunk rather than from the page HTML (which only renders 2013).
CBOE_ARCHIVE_PAGE_URL = (
    "https://www.cboe.com/markets/us/futures/market-statistics/historical-data/"
    "settlement-archive"
)
CBOE_ARCHIVE_CSV_URL = (
    "https://cdn.cboe.com/resources/futures/archive/volume-and-price/"
)
CBOE_SITE_URL = "https://www.cboe.com"

# Futures month codes, January through December
MONTH_CODES = "FGHJKMNQUVXZ"

# Matches one contract entry in the embedded list, e.g.
# {product_display:"VX F",path:"CFE_F13_VX.csv",contract_dt:"2013-01-01"}
ARCHIVE_CONTRACT_PATTERN = re.compile(
    r'\{product_display:"([^"]+)",path:"([^"]+)",contract_dt:"([^"]+)"\}'
)


def cboe_fetch_futures_contract_list_post_2013(
    root: str,
    duration_types: tuple | None,
) -> list[dict]:
    """
    Fetch the list of contracts for a Cboe futures root from the Cboe historical
    data product list. The list covers 2013 onward; earlier contracts are in the
    separate CFE archive and are not included.

    Parameters:
    -----------
    root : str
        Futures root symbol (e.g., "VX", "VXM").
    duration_types : tuple | None
        Contract duration types to keep ("M" for monthly, "W" for weekly). None
        keeps all contracts.

    Returns:
    --------
    contracts : list[dict]
        Contracts sorted by expiration date. Each dict has the keys
        product_display, expire_date, contract_dt, futures_root, duration_type,
        and path.
    """

    url = CBOE_PRODUCT_LIST_URL.format(root=root)

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        product_list = response.json()
    except Exception as e:
        print(f"Failed to fetch the contract list for {root} from {url}: {e}")
        raise

    # The product list is keyed by year, so flatten it into a single list
    contracts = [
        contract
        for year_contracts in product_list.values()
        for contract in year_contracts
    ]

    if duration_types is not None:
        contracts = [c for c in contracts if c["duration_type"] in duration_types]

    # An unknown root returns an empty product list rather than an error status
    if len(contracts) == 0:
        raise ValueError(
            f"No contracts found for {root} with duration types {duration_types} at {url}."
        )

    contracts = sorted(contracts, key=lambda c: c["expire_date"])

    return contracts


def cboe_pull_futures_data_post_2013(
    base_directory,
    root: str,
    source: str = "Cboe",
    asset_class: str = "Futures",
    timespan: str = "day",
    duration_types: tuple | None = ("M",),
    force_download: bool = False,
    pause: float = 0.5,
    verbose: bool = True,
) -> dict:
    """
    Download the daily history CSV for each contract of a Cboe futures root.

    Contracts that have expired and already have a file on disk are skipped.
    Open contracts, including one that expires today, are downloaded again on
    every run. Any failure raises immediately; files already saved are kept, so
    a re-run resumes where the failed run stopped.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    root : str
        Futures root symbol (e.g., "VX", "VXM").
    source : str
        Name of the data source (e.g., "Cboe").
    asset_class : str
        Asset class name (e.g., "Futures").
    timespan : str
        Time span of the data (e.g., "day").
    duration_types : tuple | None
        Contract duration types to pull ("M" for monthly, "W" for weekly). None
        pulls all contracts.
    force_download : bool
        If True, download every contract, including expired contracts that
        already have a file on disk.
    pause : float
        Seconds to sleep between downloads.
    verbose : bool
        If True, print a line for each contract.

    Returns:
    --------
    summary : dict
        Lists of the downloaded and skipped file names.
    """

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    os.makedirs(directory, exist_ok=True)

    contracts = cboe_fetch_futures_contract_list_post_2013(
        root=root,
        duration_types=duration_types,
    )

    print(
        f"Found {len(contracts)} {root} contracts with duration types {duration_types}."
    )

    today = date.today().isoformat()

    downloaded = []
    skipped = []

    for contract in contracts:
        file_name = os.path.basename(contract["path"])
        file_location = f"{directory}/{file_name}"
        expired = contract["expire_date"] < today

        # A closed contract's history no longer changes, so keep the existing file
        if expired and os.path.exists(file_location) and not force_download:
            skipped.append(file_name)
            if verbose == True:
                print(
                    f"Skipping {contract['product_display']} ({file_name}), expired and already saved."
                )
            continue

        url = CBOE_CDN_URL + contract["path"]

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()

            if not response.content.startswith(CSV_HEADER):
                raise ValueError(
                    f"Response does not start with the expected CSV header {CSV_HEADER!r}."
                )

            # Write to a temporary file and then move it into place, so that a
            # failed write never leaves a partial file that is later skipped
            temp_location = f"{file_location}.tmp"
            with open(temp_location, "wb") as f:
                f.write(response.content)
            os.replace(temp_location, file_location)

        except Exception as e:
            print(
                f"Failed to download {root} contract {contract['product_display']} "
                f"(expires {contract['expire_date']}) from {url}: {e}"
            )
            raise

        downloaded.append(file_name)
        if verbose == True:
            status = "expired" if expired else "open"
            print(f"Downloaded {contract['product_display']} ({file_name}), {status}.")

        time.sleep(pause)

    print(
        f"Cboe data complete for {root}: {len(downloaded)} downloaded, "
        f"{len(skipped)} skipped, saved to {directory}."
    )
    print(f"--------------------")

    return {"downloaded": downloaded, "skipped": skipped}


def cboe_fetch_futures_contract_list_pre_2013(
    root: str,
) -> list[dict]:
    """
    Fetch the list of contracts for a Cboe futures root from the Cboe historical
    data archive, which covers 2004 through 2013. The archive page renders its
    links from a contract list embedded in one of the page's JavaScript chunks,
    so the chunks are searched for that list.

    Parameters:
    -----------
    root : str
        Futures root symbol as shown on the archive page (e.g., "VX", "VM",
        "VN", "GV", "OV", "VXEM", "VXEW", "VA").

    Returns:
    --------
    contracts : list[dict]
        Contracts sorted by the contract month in the file name. Each dict has the keys
        product_display, contract_dt, futures_root, path, and url.
    """

    try:
        response = requests.get(CBOE_ARCHIVE_PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        page = response.text
    except Exception as e:
        print(f"Failed to fetch the archive page {CBOE_ARCHIVE_PAGE_URL}: {e}")
        raise

    # Chunk file names are content hashes that change when Cboe redeploys the
    # site, so find the chunk holding the contract list on every run
    chunk_paths = sorted(set(re.findall(r'/_next/static/[^"\'\s\\]+\.js', page)))

    entries = []
    for chunk_path in chunk_paths:
        url = CBOE_SITE_URL + chunk_path
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to fetch archive page script {url}: {e}")
            raise

        entries = ARCHIVE_CONTRACT_PATTERN.findall(response.text)
        if len(entries) > 0:
            break

    if len(entries) == 0:
        raise ValueError(
            f"No contract list found in the {len(chunk_paths)} scripts loaded by "
            f"{CBOE_ARCHIVE_PAGE_URL}. The page layout may have changed."
        )

    # The display name starts with the root (e.g. "VX F"); the file name does
    # not always match it (VA contracts include CFE_U06_VADL.csv)
    contracts = [
        {
            "product_display": product_display,
            "contract_dt": contract_dt,
            "futures_root": root,
            "path": path,
            "url": CBOE_ARCHIVE_CSV_URL + path,
        }
        for product_display, path, contract_dt in entries
        if product_display.split()[0] == root
    ]

    if len(contracts) == 0:
        roots = sorted(set(e[0].split()[0] for e in entries))
        raise ValueError(
            f"No archive contracts found for {root}. Roots in the archive: {roots}."
        )

    # Sort on the month code and year in the file name (CFE_F13_VX.csv); the
    # archive's contract_dt is wrong for some contracts (CFE_G12_VXEM.csv is
    # listed as 2007-02-01)
    def sort_key(contract: dict) -> tuple:
        month_code, year = contract["path"][4], int(contract["path"][5:7])
        return (year, MONTH_CODES.index(month_code), contract["path"])

    contracts = sorted(contracts, key=sort_key)

    return contracts


def cboe_pull_futures_data_pre_2013(
    base_directory,
    root: str,
    source: str = "Cboe",
    asset_class: str = "Futures",
    timespan: str = "day",
    force_download: bool = False,
    pause: float = 0.5,
    verbose: bool = True,
) -> dict:
    """
    Download the daily history CSV for each contract of a Cboe futures root from
    the Cboe historical data archive (2004 through 2013).

    Every archive contract has expired, so contracts that already have a file
    on disk are skipped. Any failure raises immediately; files already saved
    are kept, so a re-run resumes where the failed run stopped.

    Parameters:
    -----------
    base_directory : any
        Root path to store downloaded data.
    root : str
        Futures root symbol (e.g., "VX", "VM").
    source : str
        Name of the data source (e.g., "Cboe").
    asset_class : str
        Asset class name (e.g., "Futures").
    timespan : str
        Time span of the data (e.g., "day").
    force_download : bool
        If True, download every contract, including those already on disk.
    pause : float
        Seconds to sleep between downloads.
    verbose : bool
        If True, print a line for each contract.

    Returns:
    --------
    summary : dict
        Lists of the downloaded and skipped file names.
    """

    # Set file location based on parameters
    directory = f"{base_directory}/{source}/{asset_class}/{timespan}"
    os.makedirs(directory, exist_ok=True)

    contracts = cboe_fetch_futures_contract_list_pre_2013(root=root)

    print(f"Found {len(contracts)} {root} contracts in the pre-2013 archive.")

    downloaded = []
    skipped = []

    for contract in contracts:
        file_name = contract["path"]
        file_location = f"{directory}/{file_name}"

        if os.path.exists(file_location) and not force_download:
            skipped.append(file_name)
            if verbose == True:
                print(
                    f"Skipping {contract['product_display']} ({file_name}), already saved."
                )
            continue

        url = contract["url"]

        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()

            # Some archive files open with a one-line disclaimer before the
            # header, so accept the header on either of the first two lines
            first_lines = response.content.splitlines()[:2]
            if not any(line.startswith(CSV_HEADER) for line in first_lines):
                raise ValueError(
                    f"Neither of the first two lines starts with the expected CSV header {CSV_HEADER!r}."
                )

            # Write to a temporary file and then move it into place, so that a
            # failed write never leaves a partial file that is later skipped
            temp_location = f"{file_location}.tmp"
            with open(temp_location, "wb") as f:
                f.write(response.content)
            os.replace(temp_location, file_location)

        except Exception as e:
            print(
                f"Failed to download {root} archive contract {contract['product_display']} "
                f"({contract['contract_dt']}) from {url}: {e}"
            )
            raise

        downloaded.append(file_name)
        if verbose == True:
            print(f"Downloaded {contract['product_display']} ({file_name}).")

        time.sleep(pause)

    print(
        f"Cboe archive data complete for {root}: {len(downloaded)} downloaded, "
        f"{len(skipped)} skipped, saved to {directory}."
    )
    print(f"--------------------")

    return {"downloaded": downloaded, "skipped": skipped}


if __name__ == "__main__":

    # Futures roots and the contract duration types to pull for each
    # ("M" for monthly, "W" for weekly, None for all)
    roots = {
        "VX": ("M",),
        "VXM": ("M",),
    }

    for root, duration_types in roots.items():
        cboe_pull_futures_data_post_2013(
            base_directory=DATA_DIR,
            root=root,
            source="Cboe",
            asset_class="Futures",
            timespan="day",
            duration_types=duration_types,
            force_download=False,
            pause=0.5,
            verbose=True,
        )

    # Futures roots to pull from the pre-2013 archive
    archive_roots = ["VX"]

    for root in archive_roots:
        cboe_pull_futures_data_pre_2013(
            base_directory=DATA_DIR,
            root=root,
            source="Cboe",
            asset_class="Futures",
            timespan="day",
            force_download=False,
            pause=0.5,
            verbose=True,
        )
