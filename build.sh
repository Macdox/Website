#!/bin/bash
set -e

echo "Installing system dependencies..."
apt-get update -qq
apt-get install -y libzbar0

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build completed successfully!"
