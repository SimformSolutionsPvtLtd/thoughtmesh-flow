#!/usr/bin/env python3
"""
Test script to verify the /{framework}/components endpoint returns the same structure as /all
"""

import asyncio
import json
from typing import Any, Dict

import requests


async def test_endpoints_comparison():
    """Test that /{framework}/components has the same structure as /all"""
    
    base_url = "http://localhost:7860/api/v1"
    
    # You'll need to get valid auth headers - this is just a placeholder
    headers = {
        "Authorization": "Bearer YOUR_TOKEN_HERE",
        "Content-Type": "application/json"
    }
    
    try:
        # Test /all endpoint
        print("Testing /all endpoint...")
        all_response = requests.get(f"{base_url}/all", headers=headers)
        print(f"Status: {all_response.status_code}")
        
        if all_response.status_code == 200:
            all_data = all_response.json()
            print(f"All endpoint keys: {list(all_data.keys())}")
            
            # Show structure
            for category, components in all_data.items():
                if isinstance(components, dict):
                    print(f"  {category}: {len(components)} components")
                    if components:
                        # Show structure of first component
                        first_component = next(iter(components.values()))
                        print(f"    Sample component keys: {list(first_component.keys())}")
                        break
        
        # Test available frameworks first
        print("\nTesting /frameworks endpoint...")
        frameworks_response = requests.get(f"{base_url}/frameworks", headers=headers)
        print(f"Status: {frameworks_response.status_code}")
        
        if frameworks_response.status_code == 200:
            frameworks_data = frameworks_response.json()
            print(f"Available frameworks: {frameworks_data}")
            
            # Test each framework's components endpoint
            for framework in frameworks_data.get("frameworks", []):
                print(f"\nTesting /{framework}/components endpoint...")
                components_response = requests.get(f"{base_url}/frameworks/{framework}/components", headers=headers)
                print(f"Status: {components_response.status_code}")
                
                if components_response.status_code == 200:
                    components_data = components_response.json()
                    print(f"Framework {framework} endpoint keys: {list(components_data.keys())}")
                    
                    # Show structure
                    for category, components in components_data.items():
                        if isinstance(components, dict):
                            print(f"  {category}: {len(components)} components")
                            if components:
                                # Show structure of first component
                                first_component = next(iter(components.values()))
                                print(f"    Sample component keys: {list(first_component.keys())}")
                                break
                else:
                    print(f"Error: {components_response.text}")
        
    except Exception as e:
        print(f"Error: {e}")


def compare_structures(all_data: Dict[str, Any], framework_data: Dict[str, Any]) -> bool:
    """Compare the structure of /all and /{framework}/components responses"""
    
    print("\n=== STRUCTURE COMPARISON ===")
    
    # Check top-level keys
    all_categories = set(all_data.keys())
    framework_categories = set(framework_data.keys())
    
    print(f"All endpoint categories: {sorted(all_categories)}")
    print(f"Framework endpoint categories: {sorted(framework_categories)}")
    
    # Check if framework categories are subset of all categories
    if not framework_categories.issubset(all_categories):
        extra_categories = framework_categories - all_categories
        print(f"⚠️  Framework has extra categories: {extra_categories}")
    
    # Check component structure
    for category in framework_categories:
        if category in all_data and category in framework_data:
            all_components = all_data[category]
            framework_components = framework_data[category]
            
            if isinstance(all_components, dict) and isinstance(framework_components, dict):
                if all_components and framework_components:
                    # Compare structure of first component in each
                    all_component = next(iter(all_components.values()))
                    framework_component = next(iter(framework_components.values()))
                    
                    all_keys = set(all_component.keys())
                    framework_keys = set(framework_component.keys())
                    
                    print(f"\nCategory '{category}' component structure:")
                    print(f"  All endpoint keys: {sorted(all_keys)}")
                    print(f"  Framework endpoint keys: {sorted(framework_keys)}")
                    
                    if all_keys == framework_keys:
                        print(f"  ✅ Structures match for category '{category}'")
                    else:
                        missing_keys = all_keys - framework_keys
                        extra_keys = framework_keys - all_keys
                        if missing_keys:
                            print(f"  ❌ Missing keys: {missing_keys}")
                        if extra_keys:
                            print(f"  ❌ Extra keys: {extra_keys}")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_endpoints_comparison())
