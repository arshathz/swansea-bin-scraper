#!/bin/bash

# 1️⃣ Install Google Chrome (Portable)
echo "🚀 Installing Portable Chrome..."
mkdir -p /opt/chrome
wget -q -O /opt/chrome/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x /opt/chrome/chrome.deb /opt/chrome/
ln -sf /opt/chrome/opt/google/chrome/chrome /usr/local/bin/chrome

# 2️⃣ Install ChromeDriver (Manually Specify Version)
echo "🚀 Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O /opt/chrome/chromedriver.zip
unzip /opt/chrome/chromedriver.zip -d /opt/chrome/
mv /opt/chrome/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# 3️⃣ Set Chrome Environment Variables
echo "✅ Setting up Chrome environment..."
export CHROME_PATH="/usr/local/bin/chrome"
export CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"

# 4️⃣ Install Python dependencies
echo "🚀 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
