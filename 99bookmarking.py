import sys
import io
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

# Force UTF‑8 output (fixes emoji printing errors on Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:3000/api/normal-links"
LOGIN_URL_99 = "https://www.free-socialbookmarking.com/login/re-submit"
SUBMIT_URL_99 = "https://www.free-socialbookmarking.com/submit"  # <-- change if actual submit URL is different

USERNAME_99 = "nalybuxa@forexzig.com"
PASSWORD_99 = "Mannuk@12"

def fetch_api_links() -> List[str]:
    """
    Fetch links from your API and repeat them according to 'repeat'.
    """
    try:
        resp = requests.get(API_URL, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        links = []
        for entry in data:
            repeat = max(int(entry.get("repeat", 1)), 1)
            for link in entry.get("link", []):
                if isinstance(link, str) and link.strip().startswith("http"):
                    # Repeat this link `repeat` times
                    links.extend([link.strip()] * repeat)
        return links
    except Exception as e:
        print("Error fetching API links:", e)
        return []


def dismiss_fc_modal(driver):
    """
    If the monetization/ad-lock modal appears, remove it from the DOM.
    """
    try:
        # Wait a little for it to appear
        time.sleep(1)
        driver.execute_script("""
            const modal = document.querySelector('.fc-monetization-dialog-container');
            if (modal) {
                modal.remove();
            }
        """)
        # Could also remove overlay etc.
        driver.execute_script("""
            const overlay = document.querySelector('.fc-dialog-overlay');
            if (overlay) overlay.remove();
        """)
        # Optionally print for debugging
        # print("⚠️ Removed monetization modal if present")
    except Exception:
        # If no modal, or script fails, ignore
        pass


def login_99(driver: webdriver.Chrome) -> bool:
    """
    Logs in to 99bookmarking.
    """
    try:
        driver.get(LOGIN_URL_99)
        dismiss_fc_modal(driver)

        time.sleep(1)
        el_user = driver.find_element(By.ID, "username")
        el_pass = driver.find_element(By.ID, "password")

        el_user.clear()
        el_user.send_keys(USERNAME_99)
        el_pass.clear()
        el_pass.send_keys(PASSWORD_99)

        submit_btn = driver.find_element(By.CSS_SELECTOR, "form.login-form input[type='submit']")
        submit_btn.click()
        time.sleep(3)

        # After login, dismiss any modal
        dismiss_fc_modal(driver)
        # You may check if login succeeded by checking an element only visible after login
        # For now, return True
        return True
    except Exception as e:
        print("Login error (99bookmarking):", e)
        return False


def submit_one_99(driver: webdriver.Chrome, url: str) -> bool:
    """
    Submits one link on 99bookmarking after login.
    """
    try:
        driver.get(SUBMIT_URL_99)
        dismiss_fc_modal(driver)
        time.sleep(2)

        # Example: enter URL in input with id "checkUrl"
        el_url = driver.find_element(By.ID, "checkUrl")
        el_url.clear()
        el_url.send_keys(url)

        # Click continue
        btn_continue = driver.find_element(By.CSS_SELECTOR, "input.checkUrl, .checkUrl")
        btn_continue.click()
        time.sleep(2)

        dismiss_fc_modal(driver)

        # Fill title
        el_title = driver.find_element(By.ID, "articleTitle")
        el_title.clear()
        el_title.send_keys("Travel Insights " + str(random.randint(1000, 9999)))

        # Category selection (adapt as needed)
        from selenium.webdriver.support.ui import Select
        sel = Select(driver.find_element(By.ID, "category"))
        for option in sel.options:
            if "Travel" in option.text:
                option.click()
                break

        # Tags
        el_tag = driver.find_element(By.ID, "tag")
        el_tag.clear()
        el_tag.send_keys("travel, adventure, explore")

        # Description
        el_desc = driver.find_element(By.ID, "description")
        el_desc.clear()
        el_desc.send_keys("A helpful article about travel destinations and tips.")

        # Click save/continue
        save_btn = driver.find_element(By.CSS_SELECTOR, "input.saveChanges, .saveChanges")
        save_btn.click()
        time.sleep(2)

        dismiss_fc_modal(driver)

        # Final submit
        el_submit = driver.find_element(By.ID, "submit")
        el_submit.click()
        time.sleep(2)

        print(f"✅ Submitted on 99bookmarking: {url}")
        return True
    except NoSuchElementException as e:
        print("Element not found during submission (99bookmarking):", e)
        return False
    except WebDriverException as e:
        print("WebDriver error during submission (99bookmarking):", e)
        return False


def run_for_99(headless: bool = True):
    links = fetch_api_links()
    if not links:
        print("No links from API.")
        return

    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        if not login_99(driver):
            print("❌ Login failed. Aborting.")
            return

        for link in links:
            success = submit_one_99(driver, link)
            if not success:
                print("Retrying for 99bookmarking:", link)
                time.sleep(2)
                submit_one_99(driver, link)
            time.sleep(random.uniform(2, 5))
    finally:
        driver.quit()


if __name__ == "__main__":
    run_for_99(headless=True)
