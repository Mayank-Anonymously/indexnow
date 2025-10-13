import time
import random
import requests
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

API_URL = "http://localhost:3000/api/normal-links"
LOGIN_URL = "https://www.freebookmarkingsite.com/login/re-submit"
SUBMIT_URL = "https://www.freebookmarkingsite.com/submit"

USERNAME = "nalybuxa@forexzig.com"
PASSWORD = "Mannuk@12"


def fetch_api_links() -> List[str]:
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        links = []
        for entry in data:
            repeat = max(int(entry.get("repeat", 1)), 1)
            for link in entry.get("link", []):
                if isinstance(link, str) and link.strip().startswith("http"):
                    links.extend([link.strip()] * repeat)
        return links
    except Exception as exc:
        print("Error fetching API links:", exc)
        return []


def login(driver: webdriver.Chrome) -> bool:
    try:
        driver.get(LOGIN_URL)
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(USERNAME)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)

        login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        login_button.click()
        time.sleep(3)

        return "submit" in driver.current_url
    except Exception as e:
        print("Login error:", e)
        return False


def submit_one(driver: webdriver.Chrome, url: str) -> bool:
    try:
        driver.get(SUBMIT_URL)
        time.sleep(2)

        driver.find_element(By.ID, "checkUrl").clear()
        driver.find_element(By.ID, "checkUrl").send_keys(url)
        driver.find_element(By.CSS_SELECTOR, "input.checkUrl").click()
        time.sleep(3)

        driver.find_element(By.ID, "articleTitle").send_keys(
            "Top Tips for Exploring New Destinations"
        )
        category_select = driver.find_element(By.ID, "category")
        for option in category_select.find_elements(By.TAG_NAME, "option"):
            if "Travel" in option.text:
                option.click()
                break
        driver.find_element(By.ID, "tag").send_keys("travel, adventure, guide")
        driver.find_element(By.ID, "description").send_keys(
            "Explore exciting travel destinations with our comprehensive guide full of insider tips and local secrets."
        )
        driver.find_element(By.CSS_SELECTOR, "input.saveChanges").click()
        time.sleep(2)

        driver.find_element(By.ID, "submit").click()
        print(f"Submitted: {url}")
        time.sleep(2)
        return True
    except NoSuchElementException as e:
        print("Element not found:", e)
        return False
    except WebDriverException as e:
        print("WebDriver error:", e)
        return False


def run_all(headless: bool = False):
    links = fetch_api_links()
    if not links:
        print("No links to process.")
        return

    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        if not login(driver):
            print("❌ Login failed. Aborting.")
            return

        for link in links:
            success = submit_one(driver, link)
            if not success:
                print("Retrying once...")
                time.sleep(2)
                submit_one(driver, link)
            time.sleep(random.uniform(2, 5))
    finally:
        driver.quit()


if __name__ == "__main__":
    run_all(headless=False)
