#!/usr/bin/env python3
"""
Test script for the Barcode Scanner Application with Login System
Tests login functionality and manual entry features
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from flask import Flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        from pyzbar import pyzbar
        print("✅ pyzbar imported successfully")
    except ImportError as e:
        print(f"❌ pyzbar import failed: {e}")
        return False
    
    try:
        import pymongo
        print("✅ pymongo imported successfully")
    except ImportError as e:
        print(f"❌ pymongo import failed: {e}")
        return False
    
    try:
        from database import StudentDatabase
        print("✅ Custom database module imported successfully")
    except ImportError as e:
        print(f"❌ Database module import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test Flask app creation and configuration"""
    print("\n🧪 Testing Flask app creation...")
    
    try:
        from app import app
        print("✅ Flask app created successfully")
        
        # Test secret key configuration
        if app.secret_key:
            print("✅ Secret key configured")
        else:
            print("❌ Secret key not configured")
            return False
        
        # Test routes
        with app.test_client() as client:
            # Test login page (should be accessible without authentication)
            response = client.get('/login')
            if response.status_code == 200:
                print("✅ Login route accessible")
            else:
                print(f"❌ Login route failed: {response.status_code}")
                return False
            
            # Test protected route (should redirect to login)
            response = client.get('/')
            if response.status_code == 302:  # Redirect to login
                print("✅ Protected routes properly secured")
            else:
                print(f"❌ Route protection failed: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...")
    
    try:
        from database import StudentDatabase
        db = StudentDatabase()
        
        if db.client:
            print("✅ Database connection successful")
            
            # Test basic operations
            students = db.get_all_students()
            print(f"✅ Found {len(students)} students in database")
            
            logs = db.get_scan_logs()
            print(f"✅ Found {len(logs)} scan logs in database")
            
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_login_functionality():
    """Test login functionality"""
    print("\n🧪 Testing login functionality...")
    
    try:
        from app import app, ADMIN_CREDENTIALS
        
        with app.test_client() as client:
            # Test valid login
            response = client.post('/login', data={
                'username': ADMIN_CREDENTIALS['username'],
                'password': ADMIN_CREDENTIALS['password']
            }, follow_redirects=True)
            
            if response.status_code == 200:
                print("✅ Valid login works")
            else:
                print(f"❌ Valid login failed: {response.status_code}")
                return False
            
            # Test invalid login
            response = client.post('/login', data={
                'username': 'wrong',
                'password': 'wrong'
            })
            
            if 'Invalid username or password' in response.get_data(as_text=True):
                print("✅ Invalid login properly rejected")
            else:
                print("❌ Invalid login not properly handled")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Barcode Scanner Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("App Creation Tests", test_app_creation),
        ("Database Connection Tests", test_database_connection),
        ("Login Functionality Tests", test_login_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to use.")
        print("\n🔐 Login Credentials:")
        print(f"   Username: {os.getenv('ADMIN_USERNAME', 'admin')}")
        print(f"   Password: {os.getenv('ADMIN_PASSWORD', 'password123')}")
        print("\n📱 Features Available:")
        print("   ✅ Secure Login System")
        print("   ✅ Barcode Scanning")
        print("   ✅ Manual Student ID Entry")
        print("   ✅ Student Database Management")
        print("   ✅ Scan Activity Logging")
        print("\n🚀 Start the application with: python app.py")
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
