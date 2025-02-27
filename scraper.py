import os
import time
from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ Use environment variables for Chrome & ChromeDriver
CHROME_PATH = os.getenv("CHROME_PATH", "/usr/local/bin/chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

# ✅ Configure Chrome Options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = CHROME_PATH
chrome_options.add_argument("--headless")  # Ensure Chrome runs in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize Flask app
app = Flask(__name__)

def scrape_bin_data(postcode):
    """Scrapes Swansea bin collection data for a given postcode."""
    collection_details = {}

    # ✅ Initialize WebDriver
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        return {"error": f"Failed to start WebDriver: {str(e)}"}

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
            collection_details["collection_day"] = data[data.index("Collection Day:") + 1]
            collection_details["next_pink_collection"] = data[data.index("Next Pink Week Collection:") + 1]
            collection_details["next_green_collection"] = data[data.index("Next Green Week Collection:") + 1]
        except ValueError:
            collection_details["error"] = "Could not parse bin collection details."

    except Exception as e:
        collection_details["error"] = f"Scraping error: {str(e)}"

    finally:
        driver.quit()  # ✅ Close the browser

    return collection_details


@app.route("/")
def home():
    return jsonify({"message": "Bin Collection API is running!"})


@app.route("/get-bin-schedule", methods=["GET"])
def get_bin_schedule():
    """API endpoint to fetch bin collection schedule based on postcode."""
    postcode = request.args.get("postcode", "").strip()

    if not postcode:
        return jsonify({"error": "Postcode is required"}), 400

    data = scrape_bin_data(postcode)
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
