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


def oauth_signature(method, url, params, consumer_secret, token_secret=''):
    sorted_params = sorted(params.items())
    param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
    signing_key = f"{urllib.parse.quote(consumer_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    return base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()


def oauth_header(method, url, extra_params, consumer_secret, token='', token_secret=''):
    params = {
        'oauth_consumer_key': API_KEY,
        'oauth_nonce': secrets.token_urlsafe(32),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0',
    }
    if token:
        params['oauth_token'] = token

    all_params = {k: urllib.parse.quote(str(v), safe='') for k, v in {**params, **extra_params}.items()}
    params['oauth_signature'] = oauth_signature(method, url, all_params, consumer_secret, token_secret)

    return 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in params.items()])


def parse_qs(text):
    return dict(pair.split('=', 1) for pair in text.split('&') if '=' in pair)


def main():
    if not API_KEY or not API_SECRET:
        print("Error: Set TUMBLR_API_KEY and TUMBLR_API_SECRET in your environment first.")
        sys.exit(1)

    # Step 1: get request token (oob = out-of-band / PIN mode)
    header = oauth_header('POST', REQUEST_TOKEN_URL, {'oauth_callback': 'oob'}, API_SECRET)
    resp = requests.post(REQUEST_TOKEN_URL, headers={'Authorization': header})
    if not resp.ok:
        print(f"Failed to get request token: {resp.status_code} {resp.text}")
        sys.exit(1)

    req = parse_qs(urllib.parse.unquote(resp.text))
    request_token = req['oauth_token']
    request_token_secret = req['oauth_token_secret']

    # Step 2: user authorizes
    auth_url = f"{AUTHORIZE_URL}?oauth_token={request_token}"
    print(f"\nOpen this URL in your browser and authorize the app:\n\n  {auth_url}\n")
    pin = input("Paste the PIN here: ").strip()

    # Step 3: exchange PIN for access token
    header = oauth_header(
        'POST', ACCESS_TOKEN_URL,
        {'oauth_verifier': urllib.parse.quote(pin, safe='')},
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

    acc = parse_qs(urllib.parse.unquote(resp.text))
    print("\n=== SUCCESS — add these as GitHub Secrets ===")
    print(f"TUMBLR_ACCESS_TOKEN        = {acc['oauth_token']}")
    print(f"TUMBLR_ACCESS_TOKEN_SECRET = {acc['oauth_token_secret']}")


if __name__ == '__main__':
    main()
