#!/usr/bin/env python3

import asyncio
import json
import sys
from pathlib import Path

# Add the backend to the path
backend_path = Path(__file__).parent / "src" / "backend" / "base"
sys.path.insert(0, str(backend_path))

async def test_framework_components():
    """Test what the framework manager returns for agno components."""
    try:
        from langflow.core.frameworks import get_framework_manager
        
        manager = get_framework_manager()
        
        print("Getting agno components...")
        components = await manager.get_all_components(framework_filter="agno")
        
        print(f"Number of components: {len(components)}")
        
        if components:
            first_comp = components[0]
            print(f"\nFirst component type: {type(first_comp)}")
            print(f"First component: {first_comp}")
            print(f"First component attributes: {dir(first_comp)}")
            
            if hasattr(first_comp, 'name'):
                print(f"Name: {first_comp.name}")
            if hasattr(first_comp, 'display_name'):
                print(f"Display name: {first_comp.display_name}")
            if hasattr(first_comp, 'category'):
                print(f"Category: {first_comp.category}")
            if hasattr(first_comp, 'inputs'):
                print(f"Number of inputs: {len(first_comp.inputs)}")
            if hasattr(first_comp, 'outputs'):
                print(f"Number of outputs: {len(first_comp.outputs)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_framework_components()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
