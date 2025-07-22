#!/usr/bin/env python3
"""
Test script to debug API endpoints
"""

import json

import requests


def test_endpoints():
    """Test different API endpoints to understand the flow"""

    base_url = "http://localhost:7860"

    print("🔍 Testing Different API Endpoints...")

    # Test 1: /api/v1/all?framework=agno
    print("\n1. Testing /api/v1/all?framework=agno")
    try:
        response = requests.get(f"{base_url}/api/v1/all?framework=agno", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            if isinstance(data, dict):
                for category, components in data.items():
                    print(
                        f"   Category '{category}': {len(components) if isinstance(components, dict) else 'Not dict'} components"
                    )
                    if isinstance(components, dict):
                        for comp_name, comp_data in list(components.items())[:2]:  # Show first 2
                            has_template = "template" in comp_data
                            has_display_name = "display_name" in comp_data
                            print(f"     - {comp_name}: template={has_template}, display_name={has_display_name}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 2: /api/v1/frameworks?framework=agno
    print("\n2. Testing /api/v1/frameworks?framework=agno")
    try:
        response = requests.get(f"{base_url}/api/v1/frameworks?framework=agno", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {type(data)}")
            if isinstance(data, list):
                print(f"   Components count: {len(data)}")
                for i, comp in enumerate(data[:2]):  # Show first 2
                    print(f"     Component {i + 1}: {comp.get('name', 'No name')}")
                    print(f"       - display_name: {comp.get('display_name', 'Missing')}")
                    print(f"       - template: {'Yes' if 'template' in comp else 'No'}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

    # Test 3: /api/v1/frameworks (all frameworks)
    print("\n3. Testing /api/v1/frameworks")
    try:
        response = requests.get(f"{base_url}/api/v1/frameworks", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response type: {type(data)}")
            if isinstance(data, list):
                print(f"   Components count: {len(data)}")
                frameworks = set(comp.get("framework", "unknown") for comp in data)
                print(f"   Frameworks found: {frameworks}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")


if __name__ == "__main__":
    test_endpoints()
