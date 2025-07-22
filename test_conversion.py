#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add the backend to the path
backend_path = Path(__file__).parent / "src" / "backend" / "base"
sys.path.insert(0, str(backend_path))


async def test_conversion():
    """Test the component conversion logic directly."""
    try:
        print("Testing component conversion...")

        # Import framework manager
        from langflow.core.frameworks import get_framework_manager
        from langflow.core.frameworks.types import FrameworkType

        # Get manager and initialize
        manager = get_framework_manager()
        await manager.initialize()

        # Get Agno components
        components = await manager.get_all_components(framework_filter=FrameworkType.AGNO)
        print(f"Got {len(components)} Agno components")

        if components:
            first_comp = components[0]
            print(f"First component: {first_comp.name}")
            print(f"Category: {first_comp.category}")
            print(f"Inputs: {len(first_comp.inputs)}")
            print(f"Outputs: {len(first_comp.outputs)}")

            # Test the conversion logic like in the endpoint
            framework_types = {}
            category = first_comp.category.value if hasattr(first_comp.category, "value") else str(first_comp.category)

            if category not in framework_types:
                framework_types[category] = {}

            # Convert one component
            template = {"_type": first_comp.name}

            for input_def in getattr(first_comp, "inputs", []):
                field_type = getattr(input_def, "type", "str")
                input_type = "StrInput"  # Default

                # Determine the appropriate input type
                if hasattr(input_def, "options") and input_def.options:
                    input_type = "DropdownInput"
                elif field_type == "boolean":
                    input_type = "BoolInput"
                elif field_type == "number":
                    input_type = "FloatInput"
                elif field_type in ["Model", "VectorDb", "Agent", "Tool"]:
                    input_type = "HandleInput"
                elif field_type == "file":
                    input_type = "FileInput"

                # Create complete template field
                template_field = {
                    "tool_mode": False,
                    "trace_as_metadata": True,
                    "load_from_db": False,
                    "list": False,
                    "required": getattr(input_def, "required", False),
                    "placeholder": "",
                    "show": True,
                    "name": input_def.name,
                    "value": getattr(input_def, "default", None),
                    "display_name": getattr(input_def, "display_name", input_def.name.replace("_", " ").title()),
                    "type": field_type,
                    "_input_type": input_type,
                }

                # Add specific properties
                if input_type == "DropdownInput" and hasattr(input_def, "options"):
                    template_field["options"] = input_def.options
                elif input_type == "FloatInput":
                    if hasattr(input_def, "min_value") and input_def.min_value is not None:
                        template_field["min"] = input_def.min_value
                    if hasattr(input_def, "max_value") and input_def.max_value is not None:
                        template_field["max"] = input_def.max_value

                template[input_def.name] = template_field

            # Add to framework_types
            framework_types[category][first_comp.name] = {
                "template": template,
                "description": getattr(first_comp, "description", ""),
                "display_name": getattr(first_comp, "display_name", first_comp.name),
                "base_classes": [],
                "icon": getattr(first_comp, "icon", ""),
            }

            print("\nConverted structure:")
            print(f"Categories: {list(framework_types.keys())}")
            print(f"Components in {category}: {list(framework_types[category].keys())}")

            comp_data = framework_types[category][first_comp.name]
            print(f"Component has template: {'template' in comp_data}")
            print(f"Template keys: {list(comp_data['template'].keys())}")

            if len(comp_data["template"]) > 1:  # More than just _type
                first_field = next(k for k in comp_data["template"].keys() if k != "_type")
                field_data = comp_data["template"][first_field]
                print(f"First field '{first_field}' type: {field_data.get('_input_type', 'Unknown')}")
                print(f"First field keys: {list(field_data.keys())}")

            print("\n✓ Component conversion test completed!")
            return True
        else:
            print("No components found!")
            return False

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    success = await test_conversion()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
