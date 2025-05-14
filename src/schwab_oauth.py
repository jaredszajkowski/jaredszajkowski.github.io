import os
import json
import time
import base64
import webbrowser
import requests
import urllib.parse

from env_vars import load_api_keys
from pathlib import Path
from settings import config

# Load API keys from the environment
api_keys = load_api_keys()

# Add configured directories
SOURCE_DIR = config("SOURCE_DIR")

# === CONFIGURATION ===
CLIENT_ID = api_keys["SCHWAB_APP_KEY"]
CLIENT_SECRET = api_keys["SCHWAB_SECRET"]
REDIRECT_URI = "https://www.jaredszajkowski.com/schwab_callback"
TOKEN_FILE = Path(SOURCE_DIR / "token.json")

AUTH_URL = "https://api.schwabapi.com/v1/oauth/authorize"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"


# === 1. START AUTHORIZATION FLOW ===
def get_authorization_code():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print(f"\nOpen this URL and log in:\n{auth_url}")
    webbrowser.open(auth_url)

    print("\nAfter logging in, you will be redirected to:")
    print("https://www.jaredszajkowski.com/schwab_callback?code=AUTH_CODE")
    return input("Paste the value of `code=` from the URL: ").strip()


# === 2. EXCHANGE CODE FOR TOKEN ===
def exchange_code_for_token(auth_code):
    # Prepare Basic Auth header
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=payload)
    response.raise_for_status()

    tokens = response.json()
    tokens['timestamp'] = int(time.time())

    save_tokens(tokens)
    return tokens


# === 3. REFRESH TOKEN ===
def refresh_tokens(refresh_token):
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }

    response = requests.post(TOKEN_URL, headers=headers, data=payload)
    response.raise_for_status()

    tokens = response.json()
    tokens['timestamp'] = int(time.time())
    save_tokens(tokens)
    return tokens


# === 4. TOKEN HANDLING ===
def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f, indent=2)
    print(f"Tokens saved to {TOKEN_FILE}")


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)


def is_token_expired(tokens):
    expires_in = tokens.get('expires_in', 1800)
    issued_at = tokens.get('timestamp', 0)
    return time.time() > (issued_at + expires_in - 60)


# === 5. MAIN ENTRY ===
def get_access_token():
    tokens = load_tokens()

    if tokens is None:
        code = get_authorization_code()
        tokens = exchange_code_for_token(code)

    elif is_token_expired(tokens):
        print("Token expired, refreshing...")
        tokens = refresh_tokens(tokens['refresh_token'])

    return tokens['access_token']


# === 6. USAGE ===
if __name__ == "__main__":
    access_token = get_access_token()
    print("\nAccess Token:\n", access_token)
