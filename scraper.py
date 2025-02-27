import os
import time
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

# ✅ Set Chrome & ChromeDriver paths
CHROME_PATH = os.getenv("CHROME_PATH", "/usr/local/bin/chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

# ✅ Configure Chrome Options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = CHROME_PATH
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def get_driver():
    """Returns a WebDriver instance with the correct Chrome setup."""
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        return {"error": f"Failed to start WebDriver: {str(e)}"}

@app.route("/", methods=["GET"])
def home():
    """Basic API check endpoint."""
    return jsonify({"message": "Bin Collection API is running!"})

@app.route("/routes", methods=["GET"])
def list_routes():
    """Lists all available routes for debugging."""
    routes = [{"route": rule.rule, "endpoint": rule.endpoint, "methods": list(rule.methods)}
              for rule in app.url_map.iter_rules()]
    return jsonify({"routes": routes})

@app.route("/get-bin-schedule", methods=["GET"])
def get_bin_schedule():
    """Scrapes bin collection data based on user postcode."""
    postcode = request.args.get("postcode", "").strip()
    if not postcode:
        return jsonify({"error": "Missing postcode parameter."}), 400

    data = scrape_bin_data(postcode)
    return jsonify(data)

def scrape_bin_data(postcode):
    """Scrapes the Swansea Council website for bin collection schedules."""
    url = "https://www.swansea.gov.uk/recyclingsearch"
    driver = get_driver()

    if isinstance(driver, dict):  # Error handling for WebDriver
        return driver  

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # ✅ Close any popup (language selection)
        try:
            popup_close_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "dialog--active")))
            popup_close_button.click()
            time.sleep(1)  # Allow time for popup to close
        except Exception:
            pass  # No popup detected, continue

        # ✅ Switch to the iframe containing the postcode form
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)

        # ✅ Find postcode input field
        input_field = wait.until(EC.presence_of_element_located((By.ID, "c_150758422360311_input")))
        input_field.send_keys(postcode)

        # ✅ Find and click the search button
        search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "searchform__submit")))
        search_button.click()

        # ✅ Wait for results to load
        time.sleep(5)  # Adjust wait time if necessary

        # ✅ Extract bin collection details
        spans = driver.find_elements(By.TAG_NAME, "span")
        collection_details = {}

        for i in range(len(spans)):
            text = spans[i].text.strip()
            if text == "Address:":
                collection_details["address"] = spans[i + 1].text.strip()
            elif text == "Collection Day:":
                collection_details["collection_day"] = spans[i + 1].text.strip()
            elif text == "Next Pink Week Collection:":
                collection_details["next_pink_collection"] = spans[i + 1].text.strip()
            elif text == "Next Green Week Collection:":
                collection_details["next_green_collection"] = spans[i + 1].text.strip()

        driver.quit()

        if collection_details:
            return collection_details
        else:
            return {"error": "Could not find bin collection details. Website structure may have changed."}

    except Exception as e:
        driver.quit()
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
