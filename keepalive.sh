#!/bin/bash

# Keep-alive script for Render free tier
# This script pings your deployed app to prevent it from spinning down

# Replace YOUR_APP_URL with your actual Render app URL
APP_URL="https://barcode-scanner.onrender.com"

# Make a simple GET request to keep the app alive
curl -s -o /dev/null -w "%{http_code}" "$APP_URL/health" > /dev/null 2>&1

# Log the ping (optional)
echo "$(date): Pinged $APP_URL" >> /var/log/keepalive.log
