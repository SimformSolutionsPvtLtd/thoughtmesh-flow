#!/usr/bin/env python3

import requests

def test_endpoints():
    """Test different endpoints to isolate the issue."""
    try:
        print("Testing /api/v1/version...")
        response = requests.get('http://localhost:7860/api/v1/version', timeout=5)
        print(f"Version endpoint: {response.status_code}")
        
        print("Testing /api/v1/all (no framework)...")
        response = requests.get('http://localhost:7860/api/v1/all', timeout=10)
        print(f"All endpoint: {response.status_code}")
        
        print("Testing /api/v1/all?framework=all...")
        response = requests.get('http://localhost:7860/api/v1/all?framework=all', timeout=10)
        print(f"All with framework=all: {response.status_code}")
        
        print("Testing /api/v1/all?framework=invalid...")
        response = requests.get('http://localhost:7860/api/v1/all?framework=invalid', timeout=10)
        print(f"All with invalid framework: {response.status_code}")
        
        print("Testing /api/v1/all?framework=langflow...")
        response = requests.get('http://localhost:7860/api/v1/all?framework=langflow', timeout=10)
        print(f"All with langflow: {response.status_code}")
        
        print("All simple tests completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
