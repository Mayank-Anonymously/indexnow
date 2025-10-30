import requests
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

API_URL = "http://localhost:3000/api/links"
FORM_URL = "https://elektropracticum.nl/index.php?"

def run_scraper(repeat: int):
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("Failed to fetch data from API")
        return
    
    entries = response.json()

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless=new")


    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    for _ in range(repeat):
        for entry in entries:
            # Loop through all links in the array   
            all_links_html = "\n".join(entry["link"])
            message_body = f"{entry.get('message', '')}\n{all_links_html}"
            for link in entry["link"]:
                driver.get(FORM_URL)
                time.sleep(2)

                driver.find_element(By.ID, "x5gb02-topic-form-name").send_keys(entry["name"])
                driver.find_element(By.ID, "x5gb02-topic-form-email").send_keys(entry["email"])
                driver.find_element(By.ID, "x5gb02-topic-form-url").send_keys(entry.get("url", ""))
                driver.find_element(By.ID, "x5gb02-topic-form-body").send_keys(f"{entry.get('message','')}\n{message_body} ")

                driver.find_element(By.ID, "x5gb02-topic-form_submit").click()
                print(f"Submitted form for {link}")
                time.sleep(3)

    driver.quit()

if __name__ == "__main__":
    repeat = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run_scraper(repeat)
