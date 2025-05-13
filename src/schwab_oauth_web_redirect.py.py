import os
import json
import time
import webbrowser
import requests
import urllib.parse
import pkce

# === CONFIGURATION ===
CLIENT_ID = ''  # Replace with your actual Schwab client ID
REDIRECT_URI = 'https://www.jaredszajkowski.com/schwab_callback'
TOKEN_FILE = 'token.json'

AUTH_URL = 'https://api.schwabapi.com/v1/oauth2/authorize'
TOKEN_URL = 'https://api.schwabapi.com/v1/oauth2/token'


# === 1. START OAUTH FLOW AND MANUALLY GET AUTH CODE ===
def get_authorization_code():
    code_verifier, code_challenge = pkce.generate_pkce_pair()

    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }

    url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    print(f"\nOpen this URL and log in:\n{url}")
    webbrowser.open(url)

    print("\nAfter authorizing, you'll be redirected to:")
    print("https://www.jaredszajkowski.com/schwab_callback?code=AUTH_CODE")
    auth_code = input("Paste the value of `code=` from the URL: ").strip()

    return auth_code, code_verifier


# === 2. GET NEW TOKENS ===
def get_new_tokens():
    auth_code, code_verifier = get_authorization_code()

    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code_verifier': code_verifier,
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()

    tokens = response.json()
    tokens['timestamp'] = int(time.time())
    save_tokens(tokens)
    return tokens


# === 3. REFRESH TOKENS ===
def refresh_tokens(refresh_token):
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    response.raise_for_status()

    tokens = response.json()
    tokens['timestamp'] = int(time.time())
    save_tokens(tokens)
    return tokens


# === 4. SAVE / LOAD TOKENS ===
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
        print("No saved tokens found, starting auth flow...")
        tokens = get_new_tokens()

    elif is_token_expired(tokens):
        print("Access token expired, refreshing...")
        tokens = refresh_tokens(tokens['refresh_token'])

    return tokens['access_token']


# === 6. EXAMPLE USAGE ===
if __name__ == "__main__":
    token = get_access_token()
    print("\nAccess Token:\n", token)
