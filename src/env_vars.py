import os

from dotenv import load_dotenv
from pathlib import Path
from settings import config

# Get the environment variable file from the configuration
ENV_PATH = config("ENV_PATH")

def load_api_keys(
    env_path: Path=ENV_PATH
) -> dict:
    
    """
    Load API keys from a .env file.

    Parameters:
    -----------
    env_path : Path
        Path to the .env file. Default is the ENV_PATH from settings.

    Returns:
    --------
    keys : dict
        Dictionary of API keys.
    """

    load_dotenv(dotenv_path=env_path)

    keys = {
        "COINBASE_KEY": os.getenv("COINBASE_KEY"),
        "COINBASE_SECRET": os.getenv("COINBASE_SECRET"),
        "NASDAQ_DATA_LINK_KEY": os.getenv("NASDAQ_DATA_LINK_KEY"),
    }

    # Raise error if any key is missing
    for k, v in keys.items():
        if not v:
            raise ValueError(f"Missing environment variable: {k}")

    return keys
