#!/usr/bin/env python3

# Test if we can import and access Agno components directly
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "backend", "base"))

try:
    from langflow.core.frameworks.agno_components import AgnoComponentRegistry

    print("✓ Successfully imported AgnoComponentRegistry")

    components = AgnoComponentRegistry.get_all_components()
    print(f"✓ Got {len(components)} components")

    if components:
        first_comp = components[0]
        print(f"✓ First component: {first_comp.name}")
        print(f"  Category: {first_comp.category}")
        print(f"  Inputs: {len(first_comp.inputs)}")
        print(f"  Outputs: {len(first_comp.outputs)}")

        # Check if we can access the category value properly
        if hasattr(first_comp.category, "value"):
            print(f"  Category value: {first_comp.category.value}")
        else:
            print(f"  Category (no value attr): {first_comp.category}")

    print("✓ Component import test passed")

except Exception as e:
    print(f"✗ Error importing components: {e}")
    import traceback

    traceback.print_exc()
