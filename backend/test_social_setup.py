#!/usr/bin/env python3
"""
Quick test to verify social features are set up correctly
Run this after starting the backend server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test that all social endpoints are registered"""
    print("🧪 Testing Social Features Setup...\n")

    # Test 1: Check if backend is running
    print("1. Testing backend connection...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print(f"   ❌ Backend returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend. Is it running?")
        print("      Start with: uvicorn main:app --reload")
        return

    # Test 2: Check social endpoints in OpenAPI docs
    print("\n2. Checking API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        openapi = response.json()

        social_endpoints = [path for path in openapi['paths'].keys() if '/social/' in path]

        if social_endpoints:
            print(f"   ✅ Found {len(social_endpoints)} social endpoints:")
            for endpoint in social_endpoints:
                print(f"      - {endpoint}")
        else:
            print("   ❌ No social endpoints found in API docs")
            print("      Make sure social router is registered in main.py")
    except Exception as e:
        print(f"   ❌ Error checking API docs: {e}")

    # Test 3: Test public gallery endpoint (no auth needed)
    print("\n3. Testing public gallery endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/social/generations")
        if response.status_code == 200:
            generations = response.json()
            print(f"   ✅ Gallery endpoint working ({len(generations)} shared generations)")
        elif response.status_code == 500:
            print("   ❌ Server error - database tables may not be created")
            print("      Check backend logs for errors")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing gallery: {e}")

    # Test 4: Test preset marketplace endpoint
    print("\n4. Testing preset marketplace endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/social/presets")
        if response.status_code == 200:
            presets = response.json()
            print(f"   ✅ Marketplace endpoint working ({len(presets)} shared presets)")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing marketplace: {e}")

    print("\n" + "="*60)
    print("✅ Setup test complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start frontend: cd frontend && npm run dev")
    print("2. Open browser: http://localhost:3000")
    print("3. Generate a pattern and click '🔗 Share' button")
    print("4. View gallery: http://localhost:3000/gallery")
    print("5. View marketplace: http://localhost:3000/presets")
    print()

if __name__ == "__main__":
    test_endpoints()
