#!/usr/bin/env python3
"""
Fetch URLs from API (/nomal-links) and submit them to IndexNow automatically.
"""

import requests
import time
from typing import List

# -------- CONFIG --------
API_ENDPOINT = "https://your-api.com/nomal-links"  # Replace with your API endpoint
HOST = "indexnow-sooty.vercel.app"
API_KEY = "629e7928d0d9411e8a43387c18f5da20"
KEY_LOCATION = f"https://{HOST}/{API_KEY}.txt"
SEARCH_ENGINES = [
    "https://www.bing.com/indexnow",
]
DELAY_BETWEEN_SUBMISSIONS = 1.5
# ------------------------


def fetch_urls_from_api() -> List[str]:
    """Fetch URLs from your API endpoint and extract all 'link' values."""
    try:
        response = requests.get(API_ENDPOINT, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        urls = []
        for entry in data:
            entry_links = entry.get("link", [])
            if isinstance(entry_links, list):
                urls.extend(entry_links)
        return urls

    except Exception as e:
        print(f"❌ Failed to fetch URLs from API: {e}")
        return []


def submit_urls(urls: List[str]):
    """Submit a list of URLs using IndexNow."""
    if not urls:
        print("⚠️ No URLs to submit.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {
        "host": HOST,
        "key": API_KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls
    }

    for endpoint in SEARCH_ENGINES:
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Successfully submitted {len(urls)} URLs to {endpoint}")
            else:
                print(f"⚠️ Failed to submit to {endpoint} - Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            print(f"❌ Exception submitting to {endpoint}: {e}")
        time.sleep(DELAY_BETWEEN_SUBMISSIONS)


if __name__ == "__main__":
    print("Fetching URLs from API...")
    urls_to_submit = fetch_urls_from_api()

    print(f"Fetched {len(urls_to_submit)} URLs. Submitting to IndexNow...")
    submit_urls(urls_to_submit)
