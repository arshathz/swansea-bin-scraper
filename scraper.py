import os
import time
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Use manually installed Chrome & ChromeDriver paths
CHROME_PATH = os.getenv("CHROME_PATH", "/usr/local/bin/chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

# ✅ Configure Chrome Options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = CHROME_PATH
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize Flask app
app = Flask(__name__)

def get_driver():
    """Returns a WebDriver instance with the correct Chrome setup."""
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        return {"error": f"Failed to start WebDriver: {str(e)}"}

def scrape_bin_data(postcode):
    """Scrapes Swansea bin collection data for a given postcode."""
    collection_details = {}

    # ✅ Initialize WebDriver
    driver = get_driver()
    if isinstance(driver, dict):  # If there's an error, return it
        return driver

    try:
        # 🌍 Navigate to Swansea bin collection search page
        url = "https://www.swansea.gov.uk/recyclingsearch"
        driver.get(url)

        # ✅ Close language pop-up if it appears
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "dialog__close"))
            )
            close_button.click()
        except Exception:
            pass  # No pop-up appeared

        # 🔍 Find and enter postcode
        wait = WebDriverWait(driver, 10)
        input_field = wait.until(EC.presence_of_element_located((By.ID, "c_150758422360311_input")))
        input_field.clear()
        input_field.send_keys(postcode)

        # ✅ Click the search button
        search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "searchform__submitbtn")))
        search_button.click()

        # ⏳ Wait for results
        time.sleep(3)

        # ✅ Extract bin collection details
        spans = driver.find_elements(By.TAG_NAME, "span")
        data = [span.text.strip() for span in spans if span.text.strip()]

        # 📝 Parse the extracted text into structured data
        try:
            collection_details["address"] = data[data.index("Address:") + 1]
           
