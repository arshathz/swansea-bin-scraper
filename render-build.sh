#!/bin/bash

# 1️⃣ Install Google Chrome
echo "🚀 Installing Google Chrome..."
apt-get update && apt-get install -y google-chrome-stable

# 2️⃣ Install ChromeDriver (Corrected)
echo "🚀 Installing ChromeDriver..."
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O /tmp/chromedriver.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# 3️⃣ Install Python dependencies
echo "🚀 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
