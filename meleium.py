import requests
import sys
import time
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random

# Fix Unicode output issues on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:3000/api/links"
FORM_URL = "https://mmkielce.sugester.pl/Main"

def generate_random_name():
    first_names = ["John", "Alice", "David", "Emma", "Liam", "Sophia", "Noah", "Olivia", "Mason", "Ava"]
    last_names = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]
    first = random.choice(first_names)
    last = random.choice(last_names)
    number = random.randint(100, 999)
    return random.choice([f"{first}{last}{number}", f"{first}_{last}{number}", f"{first}{number}", f"{last}{number}"])

def run_scraper(repeat: int):
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("❌ Failed to fetch data from API")
        return

    entries = response.json()

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for _ in range(repeat):
        for entry in entries:
            try:
                driver.get(FORM_URL)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.main_search"))
                ).click()
                print("🟢 Clicked 'Add new suggestion' button")

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "new_post"))
                )
                print("🟢 Form appeared")

                # Fill form fields
                name_field = driver.find_element(By.ID, "post_title")
                content_field = driver.find_element(By.ID, "post_content")
                kind_select = Select(driver.find_element(By.ID, "post_kind"))

                name_field.clear()
                content_field.clear()
                kind_select.select_by_value("suggestion")

                name_field.send_keys(entry.get("name", generate_random_name()))
                content_field.send_keys(f"{entry.get('message', '')}\n" + "\n".join(entry.get("link", [])))

                # Click submit
                submit_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value*='Wyślij']"))
                )
                submit_btn.click()
                time.sleep(2)  # Wait for potential error toast

                # Check for duplicate toast
                try:
                    duplicate_toast = driver.find_element(By.CSS_SELECTOR, ".jGrowl-notification .jGrowl-message")
                    if "duplicate" in duplicate_toast.text.lower():
                        print("⚠️ Duplicate detected! Changing name and category...")
                        # Generate a new name
                        name_field.clear()
                        new_name = generate_random_name()
                        name_field.send_keys(new_name)

                        # Randomly change category (suggestion, error, question, praise)
                        kind_select.select_by_index(random.randint(0, 3))

                        # Resubmit
                        submit_btn.click()
                        print(f"🔄 Resubmitted with new name: {new_name}")
                        time.sleep(2)
                except:
                    pass

                print(f"✅ Submitted entry for: {name_field.get_attribute('value')}")
                time.sleep(3)

            except Exception as e:
                print(f"❌ Error submitting entry: {e}")
                continue

    driver.quit()

if __name__ == "__main__":
    repeat = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_scraper(repeat)
