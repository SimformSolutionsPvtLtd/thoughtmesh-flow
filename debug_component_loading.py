#!/usr/bin/env python3
"""
Debug script to check Agno component loading.
"""

import os
import sys

# Add the backend path to sys.path
backend_path = "/home/samaksh/Desktop/Projects/thoughtmesh-flow/src/backend/base"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from langflow.core.frameworks.agno_components import AgnoComponentRegistry
from langflow.core.frameworks.types import ComponentCategory


def debug_component_loading():
    """Debug component loading issues."""
    print("Debugging Agno component loading...")

    try:
        components = AgnoComponentRegistry.get_all_components()
        print(f"Total components loaded: {len(components)}")

        categories = {}
        for comp in components:
            cat = comp.category.value if hasattr(comp.category, "value") else str(comp.category)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(comp.name)

        print("\nComponents by category:")
        for cat, comps in categories.items():
            print(f"  {cat}: {len(comps)} components")
            for comp_name in comps[:3]:  # Show first 3
                print(f"    - {comp_name}")
            if len(comps) > 3:
                print(f"    ... and {len(comps) - 3} more")

        # Specifically check model components
        model_components = [comp for comp in components if comp.category == ComponentCategory.MODELS]
        print(f"\nModel components found: {len(model_components)}")

        for comp in model_components:
            print(f"\n=== {comp.display_name} ===")
            print(f"  ID: {comp.id}")
            print(f"  Category: {comp.category}")
            print(f"  Input count: {len(comp.inputs)}")
            print(f"  Output count: {len(comp.outputs)}")

            # Check for required inputs
            input_names = [inp.name for inp in comp.inputs]
            print(f"  Input names: {input_names}")

            # Check for required outputs
            output_names = [out.name for out in comp.outputs]
            print(f"  Output names: {output_names}")

            # Check output types
            for out in comp.outputs:
                if hasattr(out, "types"):
                    print(f"    {out.name} types: {out.types}")
                else:
                    print(f"    {out.name} type: {out.type} (no types attribute)")

    except Exception as e:
        print(f"Error loading components: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_component_loading()
