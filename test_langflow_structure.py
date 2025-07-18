#!/usr/bin/env python3

import requests
import json
import gzip

def test_langflow_structure():
    """Test Langflow structure to understand the expected format."""
    try:
        print("Testing /api/v1/all?framework=langflow...")
        response = requests.get('http://localhost:7860/api/v1/all?framework=langflow', timeout=30)
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error: {response.text}")
            return
            
        # Handle gzipped response
        if 'gzip' in response.headers.get('content-encoding', ''):
            data = json.loads(gzip.decompress(response.content).decode('utf-8'))
        else:
            data = response.json()
            
        print(f"Number of categories: {len(data)}")
        
        if data:
            # Get first category
            first_category = next(iter(data))
            category_data = data[first_category]
            print(f"First category: {first_category}")
            print(f"Number of components in {first_category}: {len(category_data)}")
            
            if category_data:
                # Get first component in category
                first_component_name = next(iter(category_data))
                first_component = category_data[first_component_name]
                print(f"First component: {first_component_name}")
                print(f"Component keys: {list(first_component.keys())}")
                
                # Check if it has template
                if 'template' in first_component:
                    template = first_component['template']
                    print(f"Template has {len(template)} fields")
                    
                    # Show first few template fields
                    template_fields = list(template.keys())[:5]
                    print(f"First 5 template fields: {template_fields}")
                    
                    if template_fields:
                        first_field = template[template_fields[0]]
                        print(f"First template field structure: {list(first_field.keys())}")
                
        print("✓ Langflow structure analysis complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_langflow_structure()
