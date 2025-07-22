#!/usr/bin/env python3
"""
Test to verify that Agno components have proper default values for float fields
and that the frontend can handle them without errors.
"""

import json

import requests


def test_agno_float_fields():
    """Test that Agno components have proper default values for float fields."""
    try:
        # Get Agno components
        response = requests.get("http://localhost:7860/api/v1/all?framework=agno")
        if response.status_code != 200:
            print(f"API Error: {response.status_code}")
            return False

        data = response.json()
        print(f"Found {len(data)} categories of Agno components")

        float_fields_found = 0
        float_fields_with_null_values = 0

        # Check all components for float fields
        for category_name, category_data in data.items():
            if isinstance(category_data, dict):
                for component_name, component_data in category_data.items():
                    if isinstance(component_data, dict):
                        template = component_data.get("template", {})
                        for field_name, field_data in template.items():
                            if field_data.get("type") == "float":
                                float_fields_found += 1
                                value = field_data.get("value")

                                print(f"Float field: {component_name}.{field_name}")
                                print(f"  Value: {repr(value)} (type: {type(value)})")
                                print(f"  Required: {field_data.get('required', False)}")

                                if value is None:
                                    float_fields_with_null_values += 1
                                    print(f"  ⚠️  NULL VALUE FOUND!")
                                else:
                                    print(f"  ✅ Has default value")
                                print()

        print(f"\nSummary:")
        print(f"Total float fields found: {float_fields_found}")
        print(f"Float fields with null values: {float_fields_with_null_values}")

        if float_fields_with_null_values > 0:
            print(f"⚠️  Found {float_fields_with_null_values} float fields with null values!")
            print("This could cause frontend errors if not handled properly.")
        else:
            print("✅ All float fields have default values!")

        return float_fields_with_null_values == 0

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing Agno float field default values...")
    success = test_agno_float_fields()
    exit(0 if success else 1)
