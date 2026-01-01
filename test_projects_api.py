#!/usr/bin/env python3
"""
Quick test to verify projects API is working correctly
Run this after starting the backend server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test that all projects endpoints are registered and have CORS"""
    print("Testing Projects API Setup...\n")

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
        print("      Start with: cd backend && uvicorn main:app --reload")
        return

    # Test 2: Check CORS headers on projects endpoint
    print("\n2. Testing CORS headers...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/projects",
            headers={"Origin": "http://localhost:3000"}
        )

        # Check for CORS headers
        cors_headers = {
            'access-control-allow-origin': response.headers.get('access-control-allow-origin'),
            'access-control-allow-credentials': response.headers.get('access-control-allow-credentials'),
        }

        if cors_headers['access-control-allow-origin'] == 'http://localhost:3000':
            print(f"   ✅ CORS headers present:")
            print(f"      - Origin: {cors_headers['access-control-allow-origin']}")
            print(f"      - Credentials: {cors_headers['access-control-allow-credentials']}")
        else:
            print(f"   ❌ CORS headers missing or incorrect")
            print(f"      Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Error testing CORS: {e}")

    # Test 3: Check projects endpoint requires auth
    print("\n3. Testing authentication requirement...")
    try:
        response = requests.get(f"{BASE_URL}/api/projects")
        if response.status_code == 401:
            print("   ✅ Projects endpoint requires authentication (401)")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing auth: {e}")

    # Test 4: Check OpenAPI docs
    print("\n4. Checking API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        openapi = response.json()

        project_endpoints = [path for path in openapi['paths'].keys() if '/api/projects' in path]

        if project_endpoints:
            print(f"   ✅ Found {len(project_endpoints)} project endpoints:")
            for endpoint in project_endpoints:
                methods = list(openapi['paths'][endpoint].keys())
                print(f"      - {endpoint} ({', '.join(methods)})")
        else:
            print("   ❌ No project endpoints found in API docs")
            print("      Make sure projects router is registered in main.py")
    except Exception as e:
        print(f"   ❌ Error checking API docs: {e}")

    print("\n" + "="*60)
    print("Backend API test complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. If CORS test passed, the backend is working correctly")
    print("2. Restart frontend dev server: cd frontend && npm run dev")
    print("3. Clear browser cache (Ctrl+Shift+Delete)")
    print("4. Hard reload browser (Ctrl+Shift+R)")
    print("5. Try creating a project at: http://localhost:3000/projects")
    print()

if __name__ == "__main__":
    test_endpoints()
