#!/usr/bin/env python3
"""
Test script to verify the /api/v1/all?framework=agno endpoint returns
Agno components in the correct frontend format.
"""

import json
import sys

import requests


def test_agno_endpoint():
    """Test the Agno endpoint and verify component format."""
    try:
        # Test the agno endpoint
        print("Testing /api/v1/all?framework=agno endpoint...")
        response = requests.get("http://localhost:7860/api/v1/all?framework=agno", timeout=10)

        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

        data = response.json()
        print(f"✅ API request successful (status {response.status_code})")

        # Check if we got components
        if not data:
            print("❌ No data returned from API")
            return False

        print(f"📊 Total components returned: {len(data)}")

        # Test a few components to verify format
        for i, (component_name, component_data) in enumerate(data.items()):
            if i >= 3:  # Only check first 3 components
                break

            print(f"\n🔍 Checking component: {component_name}")

            # Check required fields for frontend
            required_fields = [
                "template",
                "display_name",
                "description",
                "base_classes",
                "name",
                "input_types",
                "output_types",
            ]

            missing_fields = []
            for field in required_fields:
                if field not in component_data:
                    missing_fields.append(field)

            if missing_fields:
                print(f"  ❌ Missing required fields: {missing_fields}")
                return False
            else:
                print(f"  ✅ All required fields present")

            # Check template structure
            template = component_data.get("template", {})
            if not isinstance(template, dict):
                print(f"  ❌ Template is not a dict: {type(template)}")
                return False

            print(f"  ✅ Template is valid dict with {len(template)} fields")

            # Check a few template fields
            for field_name, field_data in list(template.items())[:2]:
                if not isinstance(field_data, dict):
                    print(f"  ❌ Template field {field_name} is not a dict: {type(field_data)}")
                    return False

                field_required = ["type", "required", "placeholder", "list", "show", "multiline", "value"]
                field_missing = [f for f in field_required if f not in field_data]
                if field_missing:
                    print(f"  ⚠️  Template field {field_name} missing: {field_missing}")
                else:
                    print(f"  ✅ Template field {field_name} has all required properties")

            # Show structure summary
            print(f"  📋 Component structure:")
            print(f"    - Display name: {component_data.get('display_name')}")
            print(f"    - Base classes: {component_data.get('base_classes')}")
            print(f"    - Input types: {component_data.get('input_types')}")
            print(f"    - Output types: {component_data.get('output_types')}")

        print(f"\n✅ All checked components have valid frontend format!")

        # Save sample for inspection
        sample_file = "agno_endpoint_sample.json"
        with open(sample_file, "w") as f:
            # Save first component as sample
            first_component = next(iter(data.items()))
            json.dump({first_component[0]: first_component[1]}, f, indent=2)
        print(f"💾 Sample component saved to {sample_file}")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend at localhost:7860")
        print("Make sure the backend is running with: make backend")
        return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False


def compare_with_langflow():
    """Compare Agno format with Langflow format."""
    try:
        print("\n" + "=" * 60)
        print("COMPARING WITH LANGFLOW FORMAT")
        print("=" * 60)

        # Get Langflow components
        print("Getting Langflow components...")
        lf_response = requests.get("http://localhost:7860/api/v1/all?framework=langflow", timeout=10)
        if lf_response.status_code != 200:
            print(f"❌ Could not get Langflow components: {lf_response.status_code}")
            return

        lf_data = lf_response.json()
        print(f"📊 Langflow components: {len(lf_data)}")

        # Get Agno components
        print("Getting Agno components...")
        agno_response = requests.get("http://localhost:7860/api/v1/all?framework=agno", timeout=10)
        if agno_response.status_code != 200:
            print(f"❌ Could not get Agno components: {agno_response.status_code}")
            return

        agno_data = agno_response.json()
        print(f"📊 Agno components: {len(agno_data)}")

        # Compare structure of first component from each
        if lf_data and agno_data:
            lf_first = next(iter(lf_data.values()))
            agno_first = next(iter(agno_data.values()))

            print(f"\n🔍 Comparing structure:")
            print(f"Langflow keys: {set(lf_first.keys())}")
            print(f"Agno keys: {set(agno_first.keys())}")

            common_keys = set(lf_first.keys()) & set(agno_first.keys())
            lf_only = set(lf_first.keys()) - set(agno_first.keys())
            agno_only = set(agno_first.keys()) - set(lf_first.keys())

            print(f"✅ Common keys ({len(common_keys)}): {common_keys}")
            if lf_only:
                print(f"⚠️  Langflow only ({len(lf_only)}): {lf_only}")
            if agno_only:
                print(f"⚠️  Agno only ({len(agno_only)}): {agno_only}")

            # Compare template structure
            lf_template = lf_first.get("template", {})
            agno_template = agno_first.get("template", {})

            print(f"\n📋 Template comparison:")
            print(f"Langflow template fields: {len(lf_template)}")
            print(f"Agno template fields: {len(agno_template)}")

            if lf_template and agno_template:
                lf_field = next(iter(lf_template.values()))
                agno_field = next(iter(agno_template.values()))

                print(f"Langflow field keys: {set(lf_field.keys())}")
                print(f"Agno field keys: {set(agno_field.keys())}")

    except Exception as e:
        print(f"❌ Error comparing formats: {e}")


if __name__ == "__main__":
    print("🧪 Testing Agno Endpoint Format")
    print("=" * 40)

    success = test_agno_endpoint()
    if success:
        compare_with_langflow()
        print(f"\n🎉 All tests passed! Agno components should now render correctly in the frontend.")
    else:
        print(f"\n❌ Tests failed. Check the issues above.")
        sys.exit(1)
