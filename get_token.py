"""
One-time OAuth 1.0a PIN flow to get Tumblr access tokens.

Usage:
  1. Set TUMBLR_API_KEY and TUMBLR_API_SECRET in your shell, then run:
       python get_token.py
  2. Visit the printed URL, authorize the app, copy the PIN.
  3. Paste the PIN when prompted.
  4. Copy the printed oauth_token and oauth_token_secret into GitHub Secrets
     as TUMBLR_ACCESS_TOKEN and TUMBLR_ACCESS_TOKEN_SECRET.
"""

import os
import sys
import hmac
import hashlib
import base64
import urllib.parse
import time
import secrets
import requests

API_KEY = os.environ.get('TUMBLR_API_KEY')
API_SECRET = os.environ.get('TUMBLR_API_SECRET')

REQUEST_TOKEN_URL = 'https://www.tumblr.com/oauth/request_token'
AUTHORIZE_URL = 'https://www.tumblr.com/oauth/authorize'
ACCESS_TOKEN_URL = 'https://www.tumblr.com/oauth/access_token'

def percent_encode(s):
    return urllib.parse.quote(str(s), safe='')

def make_signature(method, url, params, consumer_secret, token_secret=''):
    # params must be a dict of already-percent-encoded key=value pairs
    sorted_params = sorted(params.items())
    param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    base_string = f"{method}&{percent_encode(url)}&{percent_encode(param_string)}"
    signing_key = f"{percent_encode(consumer_secret)}&{percent_encode(token_secret)}"
    return base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()

def make_auth_header(method, url, extra_params, consumer_secret, token='', token_secret=''):
    """Build an OAuth 1.0a Authorization header."""
    oauth = {
        'oauth_consumer_key': API_KEY,
        'oauth_nonce': secrets.token_hex(16),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0',
    }
    if token:
        oauth['oauth_token'] = token

    # Merge all params and percent-encode both keys and values for the signature
    all_params = {}
    for k, v in {**oauth, **extra_params}.items():
        all_params[percent_encode(k)] = percent_encode(v)

    sig = make_signature(method, url, all_params, consumer_secret, token_secret)
    oauth['oauth_signature'] = sig

    # Build header string — values are percent-encoded, quoted
    parts = [f'{percent_encode(k)}="{percent_encode(v)}"' for k, v in sorted(oauth.items())]
    return 'OAuth ' + ', '.join(parts)

def parse_response(text):
    result = {}
    for pair in urllib.parse.unquote(text).split('&'):
        if '=' in pair:
            k, v = pair.split('=', 1)
            result[k] = v
    return result

def main():
    if not API_KEY or not API_SECRET:
        print("Error: Set TUMBLR_API_KEY and TUMBLR_API_SECRET in your environment first.")
        sys.exit(1)

    # Step 1: get request token (no oauth_callback — Tumblr uses the registered callback URL)
    header = make_auth_header('POST', REQUEST_TOKEN_URL, {}, API_SECRET)
    resp = requests.post(REQUEST_TOKEN_URL, headers={'Authorization': header})
    if not resp.ok:
        print(f"Failed to get request token: {resp.status_code} {resp.text}")
        sys.exit(1)

    req = parse_response(resp.text)
    request_token = req['oauth_token']
    request_token_secret = req['oauth_token_secret']

    # Step 2: user authorizes
    auth_url = f"{AUTHORIZE_URL}?oauth_token={request_token}"
    print(f"\nOpen this URL in your browser and authorize the app:\n\n  {auth_url}\n")
    print("After authorizing, Tumblr will redirect your browser to your callback URL.")
    print("The redirect URL will contain: ?oauth_token=...&oauth_verifier=XXXXXXXX")
    pin = input("Paste the oauth_verifier value here: ").strip()

    # Step 3: exchange PIN for access token
    header = make_auth_header(
        'POST', ACCESS_TOKEN_URL,
        {'oauth_verifier': pin},
        API_SECRET, request_token, request_token_secret
    )
    resp = requests.post(
        ACCESS_TOKEN_URL,
        headers={'Authorization': header},
        data={'oauth_verifier': pin}
    )
    if not resp.ok:
        print(f"Failed to get access token: {resp.status_code} {resp.text}")
        sys.exit(1)

    acc = parse_response(resp.text)
    print("\n=== SUCCESS — add these as GitHub Secrets ===")
    print(f"TUMBLR_ACCESS_TOKEN        = {acc['oauth_token']}")
    print(f"TUMBLR_ACCESS_TOKEN_SECRET = {acc['oauth_token_secret']}")

if __name__ == '__main__':
    main()
