from flask import Flask, request, jsonify
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Bin Collection API is running!"})

@app.route('/get-bin-schedule', methods=['GET'])
def get_bin_schedule():
    """
    API Endpoint: Get bin collection schedule for a given postcode.
    Example: /get-bin-schedule?postcode=SA1%206RA
    """
    postcode = request.args.get('postcode')
    if not postcode:
        return jsonify({"error": "No postcode provided"}), 400

    data = scrape_bin_data(postcode)
    return jsonify(data)

def scrape_bin_data(postcode):
    """
    Uses Selenium to scrape bin collection data from Swansea Council website.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # ✅ Run in headless mode
    options.add_argument("--no-sandbox")  # ✅ Required for running in a container
    options.add_argument("--disable-dev-shm-usage")  # ✅ Prevents memory issues

    # ✅ Use Selenium Manager to auto-detect the correct ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    collection_details = {"error": "Unknown error occurred"}

    try:
        url = "https://www.swansea.gov.uk
