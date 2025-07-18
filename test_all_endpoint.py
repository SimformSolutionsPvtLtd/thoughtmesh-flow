#!/usr/bin/env python3
"""
Test script to compare component structure from /api/v1/all endpoint
"""

import asyncio
import httpx
import json

async def test_all_endpoint():
    print("Testing /api/v1/all endpoint structure...")
    
    base_url = "http://localhost:7860"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with agno framework
            print("\n1. Testing /api/v1/all?framework=agno")
            response = await client.get(f"{base_url}/api/v1/all?framework=agno")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {response.status_code}")
                print(f"   Categories found: {list(data.keys())}")
                
                # Find first component to examine structure
                for category_name, category_components in data.items():
                    if isinstance(category_components, dict) and category_components:
                        # Get first component as sample
                        first_component_name = next(iter(category_components.keys()))
                        first_component = category_components[first_component_name]
                        print(f"   Sample component: {first_component_name}")
                        print(f"   Component keys: {list(first_component.keys())}")
                        
                        if "template" in first_component:
                            template = first_component["template"]
                            print(f"   Template keys: {list(template.keys())}")
                            
                            # Check if template has actual field definitions
                            non_type_keys = [k for k in template.keys() if k != "_type"]
                            if non_type_keys:
                                first_field = template[non_type_keys[0]]
                                print(f"   First field '{non_type_keys[0]}' structure:")
                                print(f"   {json.dumps(first_field, indent=6)}")
                            else:
                                print("   ❌ Template only contains _type, missing field definitions!")
                        break
                else:
                    print("   ❌ No components found!")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # Compare with langflow format
            print("\n2. Testing /api/v1/all?framework=langflow for comparison")
            response = await client.get(f"{base_url}/api/v1/all?framework=langflow")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {response.status_code}")
                print(f"   Categories found: {list(data.keys())}")
                
                # Find first component to examine structure
                for category_name, category_components in data.items():
                    if isinstance(category_components, dict) and category_components:
                        # Get first component as sample
                        first_component_name = next(iter(category_components.keys()))
                        first_component = category_components[first_component_name]
                        print(f"   Sample component: {first_component_name}")
                        print(f"   Component keys: {list(first_component.keys())}")
                        
                        if "template" in first_component:
                            template = first_component["template"]
                            print(f"   Template keys: {list(template.keys())}")
                            
                            # Check if template has actual field definitions
                            non_type_keys = [k for k in template.keys() if k != "_type"]
                            if non_type_keys:
                                first_field = template[non_type_keys[0]]
                                print(f"   First field '{non_type_keys[0]}' structure:")
                                print(f"   {json.dumps(first_field, indent=6)}")
                        break
                else:
                    print("   ❌ No components found!")
            else:
                print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_all_endpoint())
