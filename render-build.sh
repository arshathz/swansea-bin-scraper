#!/bin/bash

echo "🚀 Installing Google Chrome & ChromeDriver..."

# ✅ Install Chrome (Headless Version)
apt-get update && apt-get install -y wget unzip
wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i /tmp/chrome.deb || apt-get -fy install
ln -sf /usr/bin/google-chrome /usr/local/bin/chrome

# ✅ Install ChromeDriver (Matching Chrome Version)
CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O /tmp/chromedriver.zip
unzip -q /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# ✅ Export Paths
export CHROME_PATH="/usr/local/bin/chrome"
export CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

# ✅ Install Python dependencies
pip install -r requirements.txt

echo "✅ Chrome & ChromeDriver Installed Successfully!"
