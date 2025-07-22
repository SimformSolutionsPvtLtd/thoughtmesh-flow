#!/usr/bin/env python3
"""
Test script to verify the Agno endpoint data structure
"""

import json

import requests


def test_structure():
    """Test and display the structure of Agno endpoint response"""

    try:
        response = requests.get("http://localhost:7860/api/v1/all?framework=agno", timeout=10)

        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            return

        data = response.json()
        print("✅ API request successful")
        print(f"📊 Top-level structure: {type(data)}")
        print(f"📋 Categories: {list(data.keys())}")

        # Check the structure of one category
        if "Models" in data:
            models = data["Models"]
            print(f"\n🔍 Models category structure: {type(models)}")
            print(f"📊 Number of models: {len(models)}")

            # Check first model
            if models:
                first_model_name = list(models.keys())[0]
                first_model = models[first_model_name]
                print(f"\n🧪 First model: {first_model_name}")
                print(f"   Structure: {type(first_model)}")
                print(f"   Keys: {list(first_model.keys())}")

                # Check if it has template
                if "template" in first_model:
                    template = first_model["template"]
                    print(f"   Template: {type(template)}")
                    print(f"   Template keys: {list(template.keys())[:5]}...")  # First 5 keys

                # Check display_name and description
                print(f"   display_name: {first_model.get('display_name', 'MISSING')}")
                print(f"   description: {first_model.get('description', 'MISSING')[:50]}...")
                print(f"   base_classes: {first_model.get('base_classes', 'MISSING')}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_structure()
