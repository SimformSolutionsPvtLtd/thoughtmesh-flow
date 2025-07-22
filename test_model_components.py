#!/usr/bin/env python3
"""
Test script to validate Agno model component updates.
"""

import os
import sys

# Add the backend path to sys.path
backend_path = "/home/samaksh/Desktop/Projects/thoughtmesh-flow/src/backend/base"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from langflow.core.frameworks.agno_components import AgnoComponentRegistry


def test_model_component_structure():
    """Test that Agno model components have proper structure."""
    print("Testing Agno model component structure...")

    components = AgnoComponentRegistry.get_all_components()
    model_components = [comp for comp in components if comp.category.value == "models"]

    print(f"Found {len(model_components)} model components:")

    for comp in model_components:
        print(f"\n=== {comp.display_name} ===")
        print(f"ID: {comp.id}")
        print(f"Name: {comp.name}")
        print(f"Category: {comp.category}")
        print(f"Framework: {comp.framework}")

        print("\nInputs:")
        for inp in comp.inputs:
            print(f"  - {inp.name} ({inp.display_name}): {inp.type}")
            if inp.required:
                print(f"    Required: {inp.required}")
            if hasattr(inp, "default") and inp.default is not None:
                print(f"    Default: {inp.default}")

        print("\nOutputs:")
        for out in comp.outputs:
            print(f"  - {out.name} ({out.display_name}): {out.type}")
            if hasattr(out, "types"):
                print(f"    Types: {out.types}")
            if hasattr(out, "allows_loop"):
                print(f"    Allows loop: {out.allows_loop}")

        # Validate structure
        required_inputs = {"input_value", "system_message", "stream"}
        found_inputs = {inp.name for inp in comp.inputs}
        if not required_inputs.issubset(found_inputs):
            print(f"    ERROR: Missing required inputs: {required_inputs - found_inputs}")
        else:
            print(f"    ✓ Has required inputs: {required_inputs}")

        required_outputs = {"text_output", "model_output"}
        found_outputs = {out.name for out in comp.outputs}
        if not required_outputs.issubset(found_outputs):
            print(f"    ERROR: Missing required outputs: {required_outputs - found_outputs}")
        else:
            print(f"    ✓ Has required outputs: {required_outputs}")

        # Check output types
        model_output = next((out for out in comp.outputs if out.name == "model_output"), None)
        if model_output and hasattr(model_output, "types") and "LanguageModel" in model_output.types:
            print(f"    ✓ Model output has LanguageModel type")
        else:
            print(f"    ERROR: Model output missing LanguageModel type")


if __name__ == "__main__":
    test_model_component_structure()
