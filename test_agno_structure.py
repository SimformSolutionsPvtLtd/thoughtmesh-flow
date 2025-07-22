#!/usr/bin/env python3

import gzip
import json

import requests


def test_agno_structure():
    print("🔍 Testing Agno Component Structure")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:7860/api/v1/all?framework=agno", timeout=30)
        print(f"✅ API request successful (status {response.status_code})")

        if response.status_code == 200:
            # Handle gzipped response
            if response.headers.get("content-encoding") == "gzip":
                data = gzip.decompress(response.content).decode("utf-8")
                components = json.loads(data)
            else:
                components = response.json()

            print(f"📊 Response structure: {type(components)}")
            print(f"📊 Number of categories: {len(components)}")

            if components and isinstance(components, dict):
                # Look at the first category
                first_category = list(components.keys())[0]
                print(f"📂 First category: {first_category}")

                if first_category in components and components[first_category]:
                    # Look at the first component in that category
                    first_comp_name = list(components[first_category].keys())[0]
                    first_comp = components[first_category][first_comp_name]

                    print(f"🔧 First component: {first_comp_name}")
                    print(f"📋 Component type: {type(first_comp)}")
                    print(
                        f"🗝️ Component keys: {list(first_comp.keys()) if isinstance(first_comp, dict) else 'Not a dict'}"
                    )

                    # Show the actual structure
                    print(f"\n📄 Component structure:")
                    print(
                        json.dumps(first_comp, indent=2)[:500] + "..."
                        if len(json.dumps(first_comp, indent=2)) > 500
                        else json.dumps(first_comp, indent=2)
                    )

                    # Check for required fields
                    required_fields = ["template", "display_name", "description", "base_classes"]
                    missing_fields = [field for field in required_fields if field not in first_comp]

                    if missing_fields:
                        print(f"❌ Missing required fields: {missing_fields}")
                        print(f"✅ Present fields: {[field for field in required_fields if field in first_comp]}")
                    else:
                        print("✅ All required fields present!")

            else:
                print(f"❌ Unexpected response format: {components}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"📄 Response: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_agno_structure()
