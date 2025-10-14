#!/usr/bin/env python3
import time
import random
import requests
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Uncomment and set if Tesseract is not in PATH
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

GUESTBOOK_URL = "http://odins-raben.de/guestbook/sign"
API_URL = "http://localhost:3000/api/normal-links"
KEEP_BROWSER_OPEN = True  # Keep Chrome open after submissions

def preprocess_captcha(resp_content):
    img = Image.open(BytesIO(resp_content)).convert("L")
    img = ImageEnhance.Contrast(img).enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda x: 0 if x < 150 else 255, '1')
    return img

def read_captcha(driver, captcha_elem, min_length=4):
    src = captcha_elem.get_attribute("src")
    if src.startswith("/"):
        base = driver.current_url.split("//")[0] + "//" + driver.current_url.split("//")[1].split("/")[0]
        src = base + src

    print("[*] Captcha image URL:", src)

    for attempt in range(1, 11):
        resp = requests.get(src)
        img = preprocess_captcha(resp.content)
        text = pytesseract.image_to_string(
            img,
            config="--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        ).strip().replace(" ", "")
        if len(text) >= min_length:
            print(f"[*] OCR guess (attempt {attempt}): {text}")
            return text
        else:
            print(f"[!] OCR too short on attempt {attempt}, retrying...")
            time.sleep(1)
    print("[!] Failed to read CAPTCHA properly after 10 attempts.")
    return ""

def fetch_data():
    """Fetch messages and repeat them based on 'repeat' key."""
    try:
        print("[*] Fetching data from", API_URL)
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        entries = []

        if isinstance(data, dict):
            repeat = data.get("repeat", 1)
            entries = [data] * repeat
        elif isinstance(data, list):
            for item in data:
                repeat = item.get("repeat", 1)
                entries.extend([item] * repeat)
        return entries
    except Exception as e:
        print("[!] Failed to fetch API data:", e)
        return []

def submit_form(entry, driver):
    name = entry.get("name", "Guest")
    email = entry.get("email", "")
    website = entry.get("url", "")
    message = entry.get("message", "Automated submission test.")

    try:
        driver.get(GUESTBOOK_URL)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "guestbook-form-entry-form")))

        driver.find_element(By.ID, "edit-anonname").send_keys(name)
        driver.find_element(By.ID, "edit-anonemail").send_keys(email)
        driver.find_element(By.ID, "edit-anonwebsite").send_keys(website)
        driver.find_element(By.ID, "edit-message").send_keys(message)

        captcha_elem = driver.find_element(By.CLASS_NAME, "captcha_image")

        ocr_text = ""
        while not ocr_text:
            ocr_text = read_captcha(driver, captcha_elem)
            if not ocr_text:
                time.sleep(2)

        driver.find_element(By.ID, "edit-captcha-response").send_keys(ocr_text)
        driver.find_element(By.ID, "edit-submit").click()

        time.sleep(5)

        if "Die von Ihnen eingegebene Antwort war nicht passend" in driver.page_source:
            print(f"[!] CAPTCHA failed for {name}, please check manually.")
        else:
            print(f"[+] Successfully submitted form for {name}")

    except Exception as e:
        print(f"[!] Exception while submitting form for {name}:", e)

if __name__ == "__main__":
    entries = fetch_data()
    if not entries:
        print("[!] No data to process. Exiting.")
    else:
        options = Options()
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")  # keep commented for visible browser
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

        try:
            for entry in entries:
                submit_form(entry, driver)
                time.sleep(random.randint(2,5))
        except KeyboardInterrupt:
            print("[*] Script interrupted by user.")
        finally:
            if KEEP_BROWSER_OPEN:
                print("[*] Browser left open. Press Enter to quit manually.")
                input()
            driver.quit()
