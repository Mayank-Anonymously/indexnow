import requests
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# API endpoint that returns JSON data
API_URL = "http://localhost:3000/api/links"

# The form page URL
FORM_URL = "https://www.megavideomerlino.com/albatros/torneo/2010101617spadafora/default.asp?inl=0&lin=785"

def run_scraper(repeat: int):
    # Fetch entries from your local API
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("Failed to fetch data from API")
        return

    entries = response.json()

    # Chrome options setup
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    # Initialize ChromeDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for _ in range(repeat):
        for entry in entries:
            try:
                # Combine all HTML links into one string
                all_links_html = "\n".join(entry.get("link", []))
                message_body = f"{entry.get('message', '')}\n{all_links_html}"

                # Open the page
                driver.get(FORM_URL)
                time.sleep(2)

                # Fill form fields
                driver.find_element(By.NAME, "nom").send_keys(entry.get("name", ""))
                driver.find_element(By.NAME, "msg").send_keys(message_body)
                driver.find_element(By.NAME, "email").send_keys(entry.get("email", ""))
                driver.find_element(By.NAME, "url").send_keys(entry.get("url", ""))

                # Submit form
                driver.find_element(By.XPATH, "//input[@type='submit' and @value='invio']").click()
                print(f" Submitted form for {entry.get('name', '')}")

                time.sleep(3)
            except Exception as e:
                print(f" Error submitting form for {entry.get('name', '')}: {e}")
                continue

    driver.quit()

if __name__ == "__main__":
    repeat = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_scraper(repeat)
