#!/usr/bin/env python3

import requests


def test_framework_query():
    print("Testing framework parameter processing...")

    # Test with different framework values
    test_urls = [
        "http://localhost:7860/api/v1/all?framework=agno",
        "http://localhost:7860/api/v1/all?framework=langflow",
        "http://localhost:7860/api/v1/all",  # no framework
    ]

    for url in test_urls:
        print(f"\n🔗 Testing: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                # Try to get a few component names to see what we get
                if "gzip" in response.headers.get("content-encoding", ""):
                    import gzip
                    import json

                    data = json.loads(gzip.decompress(response.content).decode("utf-8"))
                else:
                    data = response.json()

                if data:
                    categories = list(data.keys())[:3]  # First 3 categories
                    print(f"   Categories: {categories}")

                    if categories:
                        first_cat = categories[0]
                        components = list(data[first_cat].keys())[:3]  # First 3 components
                        print(f"   Components in '{first_cat}': {components}")

                        # Check one component structure
                        if components:
                            comp = data[first_cat][components[0]]
                            has_template = "template" in comp
                            has_display_name = "display_name" in comp
                            print(f"   Has template: {has_template}, Has display_name: {has_display_name}")
                else:
                    print("   No data returned")
            else:
                print(f"   Error: {response.text[:100]}")

        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    test_framework_query()
