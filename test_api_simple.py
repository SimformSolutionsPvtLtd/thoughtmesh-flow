#!/usr/bin/env python3

import requests
import json
import sys

def test_api():
    try:
        print("Testing /api/v1/all?framework=agno...")
        response = requests.get('http://localhost:7860/api/v1/all?framework=agno', timeout=30)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return False
            
        data = response.json()
        print(f"Number of components: {len(data)}")
        
        if not data:
            print("No components returned!")
            return False
            
        # Check first component
        first_key = next(iter(data))
        first_component = data[first_key]
        
        print(f"\nFirst component: {first_key}")
        print(f"Component keys: {list(first_component.keys())}")
        
        # Check required fields
        required_fields = ['template', 'display_name', 'description', 'icon']
        missing_fields = []
        
        for field in required_fields:
            if field not in first_component:
                missing_fields.append(field)
            else:
                print(f"✓ Has {field}")
                
        if missing_fields:
            print(f"✗ Missing fields: {missing_fields}")
            return False
            
        # Check template structure
        if 'template' in first_component:
            template = first_component['template']
            print(f"Template has {len(template)} fields")
            
            # Check for a few template fields
            if template:
                first_template_key = next(iter(template))
                first_template_field = template[first_template_key]
                print(f"First template field: {first_template_key}")
                print(f"Template field keys: {list(first_template_field.keys())}")
                
        print("\n✓ API test passed!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
