import os
import time
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Manually specify Chrome & ChromeDriver paths
CHROME_PATH = os.getenv("CHROME_PATH", "/usr/local/bin/chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

# ✅ Configure Chrome Options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = CHROME_PATH
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# ✅ Initialize Flask app
app = Flask(__name__)

def get_driver():
    """Returns a WebDriver instance with the correct Chrome setup."""
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        return None  # Return None if WebDriver fails to
