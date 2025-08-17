#!/usr/bin/env python3
"""
Keep-alive script for Render free tier
Pings the app every 10 minutes to prevent spin-down
"""

import requests
import time
import sys
from datetime import datetime

# Replace with your actual Render app URL
APP_URL = "https://barcode-scanner.onrender.com"
PING_INTERVAL = 600  # 10 minutes in seconds

def ping_app():
    """Ping the app to keep it alive"""
    try:
        response = requests.get(f"{APP_URL}/health", timeout=30)
        status = "✅ SUCCESS" if response.status_code == 200 else f"⚠️  HTTP {response.status_code}"
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {status}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ❌ ERROR: {e}")
        return False

def main():
    """Main keep-alive loop"""
    print(f"🚀 Starting keep-alive service for {APP_URL}")
    print(f"⏰ Pinging every {PING_INTERVAL//60} minutes")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            ping_app()
            time.sleep(PING_INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Keep-alive service stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
