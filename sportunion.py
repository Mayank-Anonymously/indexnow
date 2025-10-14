#!/usr/bin/env python3
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

SITE_URL = "http://sportunion-fischbach.at/index.php?section=guestbook&cmd=post"
API_URL = "http://localhost:3000/api/normal-links"


def fetch_data():
    """Fetch entries from API and format message using link."""
    try:
        print("[*] Fetching data from", API_URL)
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            repeat = data.get("repeat", 1)
            entries = [data] * repeat
        elif isinstance(data, list):
            entries = data
        else:
            raise ValueError("Unexpected API response format.")

        # For each entry, put first link into message if available
        for entry in entries:
            links = entry.get("link", [])
            if links:
                entry["message"] = links[0]
            else:
                entry["message"] = entry.get("message") or "Automated test message."

        return entries

    except Exception as e:
        print("[!] Could not fetch API data, using fallback:", e)
        return [{
            "name": "Test User",
            "email": "user@example.com",
            "url": "https://example.com",
            "message": "Automated test message!",
            "location": "Vienna",
            "gender": "M"
        }]


def submit_form(entry):
    """Submit one guestbook entry using CAPTCHA from image title/alt."""
    name = entry.get("name", "Guest")
    email = entry.get("email", "")
    website = entry.get("url", "")
    message = entry.get("message") or "Automated submission test."
    location = entry.get("location", "Vienna")
    gender = entry.get("gender", "M")

    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # Uncomment for background execution

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    try:
        print(f"[*] Opening {SITE_URL}")
        driver.get(SITE_URL)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "GuestbookForm")))

        # Fill form fields
        driver.find_element(By.NAME, "nickname").send_keys(name)
        driver.find_element(By.NAME, "comment").send_keys((message + "\n") * 5)
        driver.find_element(By.NAME, "location").send_keys(location)
        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "url").send_keys(website)

        # Select gender
        gender_input = driver.find_element(By.XPATH, f"//input[@name='malefemale' and @value='{gender.upper()}']")
        gender_input.click()

        # Read CAPTCHA code from title/alt and remove dashes
        captcha_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src, '/images/spamprotection/')]"))
        )
        captcha_code = (captcha_elem.get_attribute("title") or captcha_elem.get_attribute("alt")).replace("-", "").strip()
        print(f"[*] CAPTCHA code detected: {captcha_code}")
        driver.find_element(By.NAME, "captcha").send_keys(captcha_code)

        # Submit form
        driver.find_element(By.NAME, "save").click()
        time.sleep(3)

        # Verify submission
        page_source = driver.page_source.lower()
        if "falsch" in page_source or "error" in page_source:
            print(f"[!] CAPTCHA failed or other error for {name}")
        else:
            print(f"[+] Successfully submitted entry for {name}")

    except Exception as e:
        print(f"[!] Exception submitting form for {name}: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    entries = fetch_data()
    if not entries:
        print("[!] No entries to process.")
    else:
        for entry in entries:
            submit_form(entry)
            time.sleep(random.randint(2, 5))  # random delay
