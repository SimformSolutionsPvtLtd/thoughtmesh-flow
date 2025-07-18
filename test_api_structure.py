#!/usr/bin/env python3

import requests
import json
import sys

def test_api_response():
    """Test the actual API response structure."""
    try:
        print("Testing /api/v1/all?framework=agno response structure...")
        response = requests.get('http://localhost:7860/api/v1/all?framework=agno', timeout=30)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return False
            
        data = response.json()
        print(f"Number of top-level keys: {len(data)}")
        
        # Print the structure
        for key, value in data.items():
            print(f"\nCategory: {key}")
            print(f"Type: {type(value)}")
            
            if isinstance(value, dict):
                print(f"Number of items: {len(value)}")
                if value:
                    first_item_key = next(iter(value))
                    first_item = value[first_item_key]
                    print(f"First item key: {first_item_key}")
                    print(f"First item type: {type(first_item)}")
                    
                    if isinstance(first_item, dict):
                        print(f"First item keys: {list(first_item.keys())}")
                    elif isinstance(first_item, list):
                        print(f"First item length: {len(first_item)}")
                        if first_item:
                            print(f"First item[0]: {first_item[0]}")
                    else:
                        print(f"First item value: {first_item}")
            elif isinstance(value, list):
                print(f"List length: {len(value)}")
                if value:
                    print(f"First list item: {value[0]}")
            else:
                print(f"Value: {value}")
                
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_response()
    sys.exit(0 if success else 1)
