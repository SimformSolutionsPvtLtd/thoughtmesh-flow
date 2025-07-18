#!/usr/bin/env python3
"""
Quick test script to verify framework filtering is working correctly.
"""

import asyncio

import aiohttp


async def test_framework_filtering():
    """Test the framework filtering endpoints."""
    base_url = "http://localhost:7860"

    async with aiohttp.ClientSession() as session:
        print("Testing framework filtering...")

        # Test 1: Get all components (should return components from both frameworks)
        print("\n1. Testing /api/v1/frameworks/components (all frameworks)")
        try:
            async with session.get(f"{base_url}/api/v1/frameworks/components") as response:
                if response.status == 200:
                    data = await response.json()
                    components = data.get("components", [])
                    frameworks = set(comp.get("framework") for comp in components)
                    print(f"   Found {len(components)} components from frameworks: {frameworks}")
                else:
                    print(f"   Error: {response.status} - {await response.text()}")
        except Exception as e:
            print(f"   Exception: {e}")

        # Test 2: Get only langflow components
        print("\n2. Testing /api/v1/frameworks/components?framework=langflow")
        try:
            async with session.get(f"{base_url}/api/v1/frameworks/components?framework=langflow") as response:
                if response.status == 200:
                    data = await response.json()
                    components = data.get("components", [])
                    frameworks = set(comp.get("framework") for comp in components)
                    print(f"   Found {len(components)} components from frameworks: {frameworks}")
                    if frameworks and frameworks != {"langflow"}:
                        print(f"   ❌ ERROR: Expected only langflow, but got: {frameworks}")
                    else:
                        print(f"   ✅ SUCCESS: Correctly filtered to langflow only")
                else:
                    print(f"   Error: {response.status} - {await response.text()}")
        except Exception as e:
            print(f"   Exception: {e}")

        # Test 3: Get only agno components
        print("\n3. Testing /api/v1/frameworks/components?framework=agno")
        try:
            async with session.get(f"{base_url}/api/v1/frameworks/components?framework=agno") as response:
                if response.status == 200:
                    data = await response.json()
                    components = data.get("components", [])
                    frameworks = set(comp.get("framework") for comp in components)
                    print(f"   Found {len(components)} components from frameworks: {frameworks}")
                    if frameworks and frameworks != {"agno"}:
                        print(f"   ❌ ERROR: Expected only agno, but got: {frameworks}")
                    else:
                        print(f"   ✅ SUCCESS: Correctly filtered to agno only")
                else:
                    print(f"   Error: {response.status} - {await response.text()}")
        except Exception as e:
            print(f"   Exception: {e}")

        # Test 4: Test invalid framework
        print("\n4. Testing /api/v1/frameworks/components?framework=invalid")
        try:
            async with session.get(f"{base_url}/api/v1/frameworks/components?framework=invalid") as response:
                if response.status == 404:
                    print(f"   ✅ SUCCESS: Correctly returned 404 for invalid framework")
                else:
                    print(f"   ❌ ERROR: Expected 404, but got {response.status}")
        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    asyncio.run(test_framework_filtering())
