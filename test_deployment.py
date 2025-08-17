#!/usr/bin/env python3
"""
Test script to verify deployment
Run this script to test if the application is working correctly
"""

import requests
import json
import sys

def test_deployment(base_url):
    """Test the deployed application"""
    
    print(f"🧪 Testing deployment at: {base_url}")
    print("=" * 50)
    
    tests = [
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "method": "GET"
        },
        {
            "name": "Home Page",
            "url": f"{base_url}/",
            "method": "GET"
        },
        {
            "name": "Students API",
            "url": f"{base_url}/api/students",
            "method": "GET"
        },
        {
            "name": "Scan Logs API",
            "url": f"{base_url}/api/scan_logs",
            "method": "GET"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            print(f"📋 Testing: {test['name']}...")
            
            response = requests.get(test['url'], timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {test['name']}: PASSED (Status: {response.status_code})")
                passed += 1
            else:
                print(f"❌ {test['name']}: FAILED (Status: {response.status_code})")
                failed += 1
                
        except requests.RequestException as e:
            print(f"❌ {test['name']}: FAILED (Error: {str(e)})")
            failed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Deployment is successful!")
        return True
    else:
        print("⚠️ Some tests failed. Check the deployment.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_deployment.py <base_url>")
        print("Example: python test_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    success = test_deployment(base_url)
    sys.exit(0 if success else 1)
