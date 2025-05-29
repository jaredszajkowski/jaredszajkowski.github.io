import os

from dotenv import load_dotenv
from pathlib import Path
from settings import config

# Get the environment variable file path from the configuration
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
        "INFURA_KEY": os.getenv("INFURA_KEY"),
        "NASDAQ_DATA_LINK_KEY": os.getenv("NASDAQ_DATA_LINK_KEY"),
        "COINBASE_KEY": os.getenv("COINBASE_KEY"),
        "COINBASE_SECRET": os.getenv("COINBASE_SECRET"),
        "SCHWAB_APP_KEY": os.getenv("SCHWAB_APP_KEY"),
        "SCHWAB_SECRET": os.getenv("SCHWAB_SECRET"),
        "SCHWAB_ACCOUNT_NUMBER_1": os.getenv("SCHWAB_ACCOUNT_NUMBER_1"),
        "SCHWAB_ENCRYPTED_ACCOUNT_ID_1": os.getenv("SCHWAB_ENCRYPTED_ACCOUNT_ID_1"),
        "SCHWAB_ACCOUNT_NUMBER_2": os.getenv("SCHWAB_ACCOUNT_NUMBER_2"),
        "SCHWAB_ENCRYPTED_ACCOUNT_ID_2": os.getenv("SCHWAB_ENCRYPTED_ACCOUNT_ID_2"),
        "SCHWAB_ACCOUNT_NUMBER_3": os.getenv("SCHWAB_ACCOUNT_NUMBER_3"),
        "SCHWAB_ENCRYPTED_ACCOUNT_ID_3": os.getenv("SCHWAB_ENCRYPTED_ACCOUNT_ID_3"),
    }

    # Raise error if any key is missing
    for k, v in keys.items():
        if not v:
            raise ValueError(f"Missing environment variable: {k}")

    return keys
