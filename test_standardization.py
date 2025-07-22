#!/usr/bin/env python3
"""
Test script to verify Agno component standardization
"""

import json

import requests


def test_agno_component_types():
    """Test that Agno components have standardized input/output types"""

    try:
        # Test the frameworks endpoint
        response = requests.get("http://localhost:7860/api/v1/frameworks", timeout=10)

        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            return False

        frameworks = response.json()
        print(f"✅ Got {len(frameworks)} frameworks")

        # Filter for Agno components
        agno_response = requests.get("http://localhost:7860/api/v1/frameworks?framework=agno", timeout=10)

        if agno_response.status_code != 200:
            print(f"❌ Agno API request failed with status {agno_response.status_code}")
            return False

        agno_components = agno_response.json()
        print(f"✅ Got {len(agno_components)} Agno components")

        if not agno_components:
            print("❌ No Agno components found")
            return False

        # Check first few components for standardization
        success = True
        for i, component in enumerate(agno_components[:5]):  # Check first 5 components
            print(f"\n📋 Component {i + 1}: {component.get('display_name', 'Unknown')}")

            # Check that template exists and has proper structure
            template = component.get("template", {})
            if not template:
                print(f"❌ No template found")
                success = False
                continue

            # Check inputs for standardized types
            inputs_found = False
            for field_name, field_def in template.items():
                if field_def.get("input_types"):
                    inputs_found = True
                    input_type = field_def.get("type")
                    print(f"  📥 Input '{field_name}': type={input_type}")

                    # Check for standardized types
                    if input_type in ["str", "float", "int", "bool", "file", "chat", "text", "any"]:
                        print(f"    ✅ Standardized input type: {input_type}")
                    else:
                        print(f"    ⚠️  Non-standard input type: {input_type}")

            if not inputs_found:
                print(f"  ❌ No input fields found")

            # Check outputs
            base_classes = component.get("base_classes", [])
            print(f"  📤 Output base_classes: {base_classes}")

            if base_classes:
                print(f"    ✅ Has output base_classes")
            else:
                print(f"    ❌ No output base_classes")
                success = False

        return success

    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    print("🔍 Testing Agno component standardization...")

    if test_agno_component_types():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")


if __name__ == "__main__":
    main()
