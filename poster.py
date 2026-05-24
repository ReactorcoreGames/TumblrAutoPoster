import csv
import json
import os
import sys
import requests
import hmac
import hashlib
import base64
import urllib.parse
import time
import secrets
from datetime import datetime, timezone

CSV_FILE = 'posts.csv'
STATE_FILE = 'state.json'
API_KEY = os.environ.get('TUMBLR_API_KEY')
API_SECRET = os.environ.get('TUMBLR_API_SECRET')
ACCESS_TOKEN = os.environ.get('TUMBLR_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('TUMBLR_ACCESS_TOKEN_SECRET')
BLOG_NAME = os.environ.get('TUMBLR_BLOG_NAME')
REPO_ACTOR = os.environ.get('GITHUB_ACTOR', 'github-actions[bot]')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')


def create_oauth_signature(method, url, params, api_secret, token_secret):
    sorted_params = sorted(params.items())
    param_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
    signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    signature = base64.b64encode(
        hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
    ).decode()
    return signature

def create_oauth_header(method, url, params=None):
    if params is None:
        params = {}
    oauth_params = {
        'oauth_consumer_key': API_KEY,
        'oauth_nonce': secrets.token_urlsafe(32),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': ACCESS_TOKEN,
        'oauth_version': '1.0'
    }
    all_params = {**oauth_params, **params}
    encoded_params = {k: urllib.parse.quote(str(v), safe='') for k, v in all_params.items()}
    signature = create_oauth_signature(method, url, encoded_params, API_SECRET, ACCESS_TOKEN_SECRET)
    oauth_params['oauth_signature'] = signature
    oauth_header = 'OAuth ' + ', '.join([f'{k}="{urllib.parse.quote(str(v), safe="")}"' for k, v in oauth_params.items()])
    return oauth_header

def main():
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BLOG_NAME]):
        print("Error: Missing Tumblr API credentials. Need:")
        print("- TUMBLR_API_KEY")
        print("- TUMBLR_API_SECRET")
        print("- TUMBLR_ACCESS_TOKEN")
        print("- TUMBLR_ACCESS_TOKEN_SECRET")
        print("- TUMBLR_BLOG_NAME")
        sys.exit(1)

    try:
        posts = load_posts()
        if not posts:
            print("No posts found in CSV.")
            sys.exit(0)

        state = load_state()
        last_index = state.get('last_row_index', -1)
        next_index = last_index + 1

        if next_index >= len(posts):
            print("All posts published.")
            sys.exit(0)

        post = posts[next_index]
        title = post.get('title', '').strip()
        url = post.get('url', '').strip()
        hashtags = post.get('hashtags', '').strip()

        if not title or not url:
            print(f"Error: Missing title or URL in row {next_index + 2}")
            sys.exit(1)

        tags = [t.lstrip('#') for t in hashtags.split() if t]

        print(f"Posting row {next_index + 2}: {title}")
        post_to_tumblr(title, url, tags)
        update_state(next_index)
        commit_changes(next_index)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def load_posts():
    try:
        with open(CSV_FILE, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        sys.exit(1)

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {STATE_FILE}. Starting from beginning.")
            return {}
        except Exception as e:
            print(f"Error reading state file: {str(e)}. Starting from beginning.")
            return {}
    return {}

def post_to_tumblr(title, url, tags):
    try:
        endpoint = f'https://api.tumblr.com/v2/blog/{BLOG_NAME}/posts'
        headers = {
            'Authorization': create_oauth_header('POST', endpoint),
            'Content-Type': 'application/json'
        }
        body = {
            "content": [
                {
                    "type": "link",
                    "url": url,
                    "title": title,
                    "description": title
                }
            ],
            "tags": tags,
            "state": "published"
        }
        resp = requests.post(endpoint, headers=headers, json=body)
        resp.raise_for_status()
        post_id = resp.json().get('response', {}).get('id')
        print(f"Post published successfully! Post ID: {post_id}")
        return True
    except requests.RequestException as e:
        print(f"Error posting to Tumblr: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)

def update_state(next_index):
    try:
        new_state = {
            'last_row_index': next_index,
            'last_post_time': datetime.now(timezone.utc).isoformat()
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_state, f, indent=2)
        print(f"State updated: {new_state}")
    except Exception as e:
        print(f"Error updating state file: {str(e)}")
        sys.exit(1)

def commit_changes(next_index):
    try:
        commit_message = f'Update state.json after posting row {next_index + 2}'
        os.system(f'git config user.name "{REPO_ACTOR}"')
        os.system(f'git config user.email "{REPO_ACTOR}@users.noreply.github.com"')
        os.system(f'git add {STATE_FILE}')
        os.system(f'git commit -m "{commit_message}"')
        if GITHUB_TOKEN:
            origin_url = f'https://x-access-token:{GITHUB_TOKEN}@github.com/{os.environ.get("GITHUB_REPOSITORY")}.git'
            os.system(f'git remote set-url origin {origin_url}')
        os.system('git push')
        print("Changes committed and pushed successfully")
    except Exception as e:
        print(f"Error committing changes: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
