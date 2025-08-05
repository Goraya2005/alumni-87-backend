#!/usr/bin/env python3
"""
Backend API Test Script
This script tests the main API endpoints to ensure everything is working correctly
"""

import requests
import json
import sys
import os

# Configuration
BASE_URL = os.getenv("TEST_URL", "http://localhost:8000")
TEST_USER = {
    "username": "testuser123",
    "email": "test@example.com", 
    "password": "testpass123",
    "name": "Test User",
    "registration_number": "TEST001",
    "department": "Plant Breeding",
    "address": "Test Address",
    "city": "Test City",
    "country": "Test Country",
    "phone": "+1234567890",
    "bio": "Test user for API testing"
}

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✓ User registration passed")
            return True, response.json()
        else:
            print(f"✗ User registration failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"✗ User registration failed: {e}")
        return False, None

def test_user_login():
    """Test user login"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/users/token",
            data={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            print("✓ User login passed")
            token_data = response.json()
            return True, token_data.get("access_token")
        else:
            print(f"✗ User login failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"✗ User login failed: {e}")
        return False, None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/members",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        if response.status_code == 200:
            members = response.json()
            print(f"✓ Protected endpoint access passed ({len(members)} members found)")
            return True
        else:
            print(f"✗ Protected endpoint access failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Protected endpoint access failed: {e}")
        return False

def cleanup_test_user():
    """Clean up test user (requires admin access)"""
    print("Note: Test user cleanup requires manual intervention")

def main():
    """Main test function"""
    print("PBG87 Backend API Test")
    print("=" * 40)
    print(f"Testing URL: {BASE_URL}")
    print("-" * 40)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Health check
    if test_health_check():
        success_count += 1
    
    # Test 2: User registration
    reg_success, user_data = test_user_registration()
    if reg_success:
        success_count += 1
    
    # Test 3: User login
    login_success, token = test_user_login()
    if login_success:
        success_count += 1
    
    # Test 4: Protected endpoint (only if login succeeded)
    if login_success and token:
        if test_protected_endpoint(token):
            success_count += 1
    else:
        print("✗ Skipped protected endpoint test (login failed)")
    
    # Results
    print("-" * 40)
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("✓ All tests passed! Backend is working correctly.")
        return True
    else:
        print("✗ Some tests failed. Check the backend configuration.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    success = main()
    sys.exit(0 if success else 1)
