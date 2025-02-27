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
        url = "https://www.swansea.gov.uk/recyclingsearch"
        print(f"🌍 Navigating to {url}...")

        driver.get(url)
        time.sleep(3)

        # ✅ Step 1: Close the language popup if it appears
        try:
            popup = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "language-choice-prompt"))
            )
            print("✅ Language popup detected. Closing it...")
            close_button = popup.find_element(By.TAG_NAME, "button")
            close_button.click()
            time.sleep(2)
        except:
            print("ℹ️ No language popup detected.")

        # ✅ Step 2: Switch into the iframe
        print("🔍 Waiting for iframe...")
        wait = WebDriverWait(driver, 10)
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        print("✅ Switched to iframe!")

        # ✅ Step 3: Locate and enter postcode
        print("⌛ Searching for postcode input field...")
        try:
            input_field = wait.until(EC.presence_of_element_located((By.ID, "txtPostCode")))
            print("✅ Found postcode input field. Entering postcode...")
            input_field.clear()
            input_field.send_keys(postcode)
        except Exception as e:
            print("❌ Could not find postcode input field:", e)
            collection_details["error"] = "Postcode input field not found inside iframe."
            return collection_details

        # ✅ Step 4: Click the search button
        print("⌛ Searching for search button inside iframe...")
        try:
            search_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSearch")))
            print("✅ Found search button. Clicking...")
            search_button.click()
        except Exception as e:
            print("❌ Could not find search button:", e)
            collection_details["error"] = "Search button not found inside iframe."
            return collection_details

        # ✅ Step 5: Wait for results to load
        print("⌛ Waiting for results inside iframe...")
        time.sleep(5)

        # ✅ Step 6: Extract bin collection details using XPath
        print("📌 Extracting bin collection data...")
        try:
            address_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Address:')]/following-sibling::span")
            collection_day_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Collection Day:')]/following-sibling::span")
            next_pink_collection_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Next Pink Week Collection:')]/following-sibling::span")
            next_green_collection_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Next Green Week Collection:')]/following-sibling::span")

            collection_details = {
                "address": address_element.text.strip() if address_element else "Not found",
                "collection_day": collection_day_element.text.strip() if collection_day_element else "Not found",
                "next_pink_collection": next_pink_collection_element.text.strip() if next_pink_collection_element else "Not found",
                "next_green_collection": next_green_collection_element.text.strip() if next_green_collection_element else "Not found"
            }
            print("✅ Successfully extracted bin collection data!")

        except Exception as e:
            print("❌ Error extracting bin details:", e)
            collection_details["error"] = "Could not find bin collection details. Website structure may have changed."

    except Exception as e:
        print("❌ Error in WebDriver execution:", e)
        collection_details["error"] = str(e)

    finally:
        driver.quit()
        print("🚪 WebDriver closed.")

    return collection_details

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Running Flask on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
