#!/usr/bin/env python3
"""
Automated Gästebuch form submitter
Fetches link data from http://localhost:3000/api/links
and posts to http://www.thepages-show.com/gaestebuch.php?action=entry
"""

import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sys

# ---------------- Configuration ---------------- #
API_URL = "http://localhost:3000/api/normal-links"
FORM_URL = "http://www.thepages-show.com/gaestebuch.php?action=entry"
WAIT_TIME = 2  # seconds to wait for form to load or after submit
# ------------------------------------------------ #

# Fix Windows Unicode issue
sys.stdout.reconfigure(encoding='utf-8')


def solve_spam(driver):
    """Detect and solve math spam-check question like '9 + 1 ='."""
    html = driver.page_source
    match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", html)
    if not match:
        print("[WARN] Spam-check not found!")
        return ""
    a, op, b = match.groups()
    a, b = int(a), int(b)
    result = {
        "+": a + b,
        "-": a - b,
        "*": a * b,
        "/": a / b if b != 0 else 0
    }.get(op, 0)
    print(f"[INFO] Solved spam-check: {a} {op} {b} = {result}")
    return str(result)


def run_scraper():
    """Fetch API data and submit forms repeatedly."""
    print("[INFO] Fetching data from API...")
    response = requests.get(API_URL)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch API data (status {response.status_code})")
        return
    entries = response.json()

    # Launch Chrome (visible)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Process each entry from API
    for entry in entries:
        name = entry.get("name", "")
        email = entry.get("email", "")
        url = entry.get("url", "")
        message = entry.get("message", "")
        links = entry.get("link", [])
        repeat = int(entry.get("repeat", 1))

        print(f"\n[INFO] Starting submission for {name} - repeating {repeat} time(s)")

        for r in range(repeat):
            for link in links:
                print(f"[INFO] Round {r + 1}/{repeat} - submitting link: {link}")
                driver.get(FORM_URL)
                time.sleep(WAIT_TIME)

                # Fill form fields
                driver.find_element(By.NAME, "name").send_keys(name)
                driver.find_element(By.NAME, "email_hp").send_keys(email)
                driver.find_element(By.NAME, "text").send_keys(f"{k}\n{link}")

                # Solve spam check
                spam_result = solve_spam(driver)
                spam_field = driver.find_element(By.NAME, "spam_check")
                spam_field.clear()
                spam_field.send_keys(spam_result)

                # Submit the form
                driver.find_element(By.NAME, "entry").click()
                print(f"[OK] Submitted form for {name} ({link}) - iteration {r + 1}/{repeat}")
                time.sleep(WAIT_TIME * 2)

    driver.quit()
    print("\n[INFO] All form submissions completed successfully!")


if __name__ == "__main__":
    run_scraper()
