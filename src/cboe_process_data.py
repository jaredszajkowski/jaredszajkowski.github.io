"""
This script uses existing functions to download futures and index data from
Cboe and save it under DATA_DIR/Cboe. Each data type has its own section, run
in this order by main():

* pull_futures: futures roots in GLOBAL_FUTURES_ROOTS (e.g. VX, VXM)
    * Download the daily history CSV for each contract from 2013 onward
    * Download the daily history CSV for each contract in the pre-2013
      archive, for the roots in GLOBAL_ARCHIVE_ROOTS
* pull_indices: index symbols in GLOBAL_INDEX_SYMBOLS (e.g. VIX, VIX3M)
    * Download the full daily history CSV for each index

Cboe needs no API key and has no rate limit tiers, so every section pauses
GLOBAL_PAUSE seconds between downloads. Expired futures contracts that are
already on disk are skipped unless GLOBAL_FORCE_DOWNLOAD is True; open
contracts and every index file are downloaded again on each run.

Files are saved as the raw CSVs Cboe serves, under
DATA_DIR/Cboe/<asset_class>/day.
"""

from cboe_pull_futures_data import (
    cboe_pull_futures_data_post_2013,
    cboe_pull_futures_data_pre_2013,
)
from cboe_pull_index_data import cboe_pull_index_data
from settings import config

# Get the environment variable for where data is stored
DATA_DIR = config("DATA_DIR")

# Set global variables
GLOBAL_FORCE_DOWNLOAD = False
GLOBAL_PAUSE = 0.5
GLOBAL_VERBOSE = True

# Futures roots and the contract duration types to pull for each
# ("M" for monthly, "W" for weekly, None for all)
GLOBAL_FUTURES_ROOTS = {
    "VX": ("M",),
    "VXM": ("M",),
}

# Futures roots to pull from the pre-2013 archive
GLOBAL_ARCHIVE_ROOTS = ["VX"]

# Cboe indices to pull
GLOBAL_INDEX_SYMBOLS = [
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


def pull_futures():
    """Pull contract data for the futures roots, from 2013 onward and from the archive."""

    # Contracts from 2013 onward
    for root, duration_types in GLOBAL_FUTURES_ROOTS.items():
        cboe_pull_futures_data_post_2013(
            base_directory=DATA_DIR,
            root=root,
            source="Cboe",
            asset_class="Futures",
            timespan="day",
            duration_types=duration_types,
            force_download=GLOBAL_FORCE_DOWNLOAD,
            pause=GLOBAL_PAUSE,
            verbose=GLOBAL_VERBOSE,
        )

    # Contracts from the pre-2013 archive
    for root in GLOBAL_ARCHIVE_ROOTS:
        cboe_pull_futures_data_pre_2013(
            base_directory=DATA_DIR,
            root=root,
            source="Cboe",
            asset_class="Futures",
            timespan="day",
            force_download=GLOBAL_FORCE_DOWNLOAD,
            pause=GLOBAL_PAUSE,
            verbose=GLOBAL_VERBOSE,
        )


def pull_indices():
    """Pull the full daily history for the index symbols."""

    cboe_pull_index_data(
        base_directory=DATA_DIR,
        symbols=GLOBAL_INDEX_SYMBOLS,
        source="Cboe",
        asset_class="Indices",
        timespan="day",
        pause=GLOBAL_PAUSE,
        verbose=GLOBAL_VERBOSE,
    )


def main():
    pulls = [
        pull_futures,
        pull_indices,
    ]

    for pull in pulls:
        pull()


if __name__ == "__main__":
    main()
