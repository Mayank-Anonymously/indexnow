#!/usr/bin/env python3
"""
Selenium form submitter for form with IDs like x5gb432-*
Based on your provided form structure.

Usage:
    pip install selenium webdriver-manager requests
    python submit_form_x5gb432.py [repeat]

Notes:
 - Run only on sites you control or have permission for.
 - Script WILL NOT solve CAPTCHAs.
"""

import requests
import sys
import time
import random
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# -------- CONFIG --------
API_URL = "http://localhost:3000/api/links"   # your API returning entries list
FORM_URL = "http://www.metallbau-willeke.de/kunden.php?"
HEADLESS = True
IMPLICIT_WAIT = 8
EXPLICIT_WAIT = 15
DELAY_MIN = 1.0
DELAY_MAX = 2.5
# ------------------------


def random_sleep(a=DELAY_MIN, b=DELAY_MAX):
    """Pause randomly to simulate human behavior."""
    time.sleep(a + random.random() * (b - a))


def create_driver(headless: bool = HEADLESS):
    """Initialize Chrome WebDriver."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver


def detect_captcha(driver) -> bool:
    """Detect presence of CAPTCHA elements."""
    captcha_selectors = [
        "iframe[src*='recaptcha']",
        ".g-recaptcha",
        "input[name='captcha']",
        "img[src*='captcha']",
        "div.h-captcha",
        "iframe[src*='hcaptcha']",
    ]
    return any(driver.find_elements(By.CSS_SELECTOR, sel) for sel in captcha_selectors)


def fetch_entries(api_url: str) -> List[dict]:
    """Fetch data from API."""
    r = requests.get(api_url, timeout=20)
    r.raise_for_status()
    return r.json()


def submit_one_entry(driver, entry: dict):
    """
    Fill and submit one entry.

    entry format:
    {
      "name": "Name",
      "email": "email@example.com",
      "url": "https://example.com",
      "message": "Message text",
      "link": ["https://one.example/"]
    }
    """
    driver.get(FORM_URL)
    wait = WebDriverWait(driver, EXPLICIT_WAIT)

    # Wait for form
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form#x5gb432-topic-form")))
    except Exception as e:
        print(" Form not found:", e)
        return False

    random_sleep()

    # CAPTCHA check before filling
    if detect_captcha(driver):
        print(" CAPTCHA detected. Manual solving required.")
        return False

    # Fill name
    try:
        name_el = driver.find_element(By.ID, "x5gb432-topic-form-name")
        name_el.clear()
        name_el.send_keys(entry.get("name", "Test User"))
    except Exception as ex:
        print("Name field error:", ex)

    random_sleep()

    # Fill email
    try:
        email_el = driver.find_element(By.ID, "x5gb432-topic-form-email")
        email_el.clear()
        email_el.send_keys(entry.get("email", "test@example.com"))
    except Exception as ex:
        print("Email field error:", ex)

    random_sleep()

    # Fill URL (optional)
    try:
        url_el = driver.find_element(By.ID, "x5gb432-topic-form-url")
        url_el.clear()
        url_el.send_keys(entry.get("url", ""))
    except Exception:
        pass

    random_sleep()

    # Prepare message body
    links = entry.get("link", []) or []
    link_texts = [f'<a href="{link}">{link}</a>' for link in links]
    links_html = "\n".join(link_texts)

    message = entry.get("message", "")
    final_body = f"{message}\n\n{links_html}" if links_html else message

    try:
        body_el = driver.find_element(By.ID, "x5gb432-topic-form-body")
        body_el.clear()
        body_el.send_keys(final_body)
    except Exception as ex:
        print("Textarea error:", ex)

    random_sleep()

    # Clear honeypot fields
    try:
        prt_els = driver.find_elements(By.CSS_SELECTOR, "input.prt_field, input[name='prt']")
        for e in prt_els:
            driver.execute_script("arguments[0].value = '';", e)
    except Exception:
        pass

    random_sleep()

    # Check CAPTCHA again
    if detect_captcha(driver):
        print(" CAPTCHA appeared after filling.")
        return False

    #  Proper form submission using JavaScript click
    try:
        submit_btn = driver.find_element(By.ID, "x5gb432-topic-form_submit")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        random_sleep(0.5, 1.0)
        driver.execute_script("arguments[0].click();", submit_btn)
        print(" Clicked 'Senden' button successfully.")
    except Exception as ex:
        print(" Could not click 'Senden':", ex)
        return False

    # Wait for potential redirect/confirmation
    time.sleep(3)
    print(f" Submitted entry for: {entry.get('name', 'unknown')} ({entry.get('email', '')})")
    return True


def run_scraper(repeat: int = 1):
    """Main runner."""
    try:
        entries = fetch_entries(API_URL)
    except Exception as e:
        print("Failed to fetch entries:", e)
        return

    driver = create_driver(HEADLESS)
    success_count = 0
    try:
        for _ in range(repeat):
            for entry in entries:
                ok = submit_one_entry(driver, entry)
                if ok:
                    success_count += 1
                random_sleep(2.0, 5.0)
    finally:
        if not HEADLESS:
            print("Done. Browser left open for inspection. Close it manually.")
        else:
            driver.quit()
        print(f" Total successful submissions: {success_count}")


if __name__ == "__main__":
    repeat = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_scraper(repeat)
