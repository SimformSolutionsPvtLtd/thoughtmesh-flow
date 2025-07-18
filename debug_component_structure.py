#!/usr/bin/env python3
"""
Debug script to compare Langflow vs Agno component structures
"""

import asyncio
import json
from langflow.interface.components import get_and_cache_all_types_dict
from langflow.services.deps import get_settings_service
from langflow.core.frameworks import get_framework_manager

async def main():
    print("=== Debug Component Structure ===\n")
    
    # Get all types (standard Langflow format)
    settings_service = get_settings_service()
    all_types = await get_and_cache_all_types_dict(settings_service)
    
    # Print sample Langflow component structure
    print("=== LANGFLOW COMPONENT STRUCTURE ===")
    for category_name, category_components in all_types.items():
        if isinstance(category_components, dict) and category_components:
            # Get first component as sample
            first_component_name = next(iter(category_components.keys()))
            first_component = category_components[first_component_name]
            print(f"Category: {category_name}")
            print(f"Component: {first_component_name}")
            print(f"Structure keys: {list(first_component.keys())}")
            if "template" in first_component:
                template = first_component["template"]
                print(f"Template keys: {list(template.keys())}")
                if template:
                    # Show first template field structure
                    for field_name, field_data in template.items():
                        if isinstance(field_data, dict) and field_name != "_type":
                            print(f"Field '{field_name}' structure: {list(field_data.keys())}")
                            break
            print("Full component structure:")
            print(json.dumps(first_component, indent=2, default=str)[:500] + "...")
            break
    
    print("\n" + "="*60 + "\n")
    
    # Get Agno components via framework manager
    print("=== AGNO COMPONENT STRUCTURE ===")
    manager = get_framework_manager()
    if not manager._initialized:
        await manager.initialize()
    
    if "agno" in manager.get_available_frameworks():
        agno_components = await manager.get_all_components(framework_filter="agno")
        
        if agno_components:
            first_comp = agno_components[0]
            print(f"Component: {first_comp.name}")
            print(f"ComponentMetadata attributes:")
            for attr in dir(first_comp):
                if not attr.startswith('_'):
                    value = getattr(first_comp, attr)
                    print(f"  {attr}: {type(value)} = {value}")
            
            # Show how it's being converted in the API
            print(f"\nConverted to API format:")
            api_format = {
                "type": first_comp.name,
                "base_classes": getattr(first_comp, "base_classes", []),
                "template": {
                    "inputs": getattr(first_comp, "inputs", {}),
                    "outputs": getattr(first_comp, "outputs", {}),
                },
                "description": getattr(first_comp, "description", ""),
                "display_name": first_comp.name,
                "framework": "agno",
                "version": getattr(first_comp, "version", "1.0.0"),
            }
            print(json.dumps(api_format, indent=2, default=str))
    else:
        print("Agno framework not available")

if __name__ == "__main__":
    asyncio.run(main())
