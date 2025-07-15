"""Example usage and demonstration of the Framework Abstraction System."""

import asyncio
from typing import Any

from langflow.core.frameworks import (
    FrameworkType,
    get_framework_execution_enhancer,
    get_framework_integrator,
    get_framework_manager,
)


async def demonstrate_framework_system():
    """Demonstrate the key features of the framework abstraction system."""
    print("Framework Abstraction System Demonstration")
    print("=" * 50)

    # 1. Get the initialized framework manager
    manager = get_framework_manager()

    # Initialize the manager if not already done
    if not manager._initialized:
        await manager.initialize()

    print(f"Available frameworks: {list(manager.get_available_frameworks())}")

    # 2. Discover components for each framework
    for framework in manager.get_available_frameworks():
        print(f"\n{framework.value} Framework:")
        try:
            components = await manager.discover_components(framework)
            print(f"  Found {len(components)} components")
            for component in components[:3]:  # Show first 3 components
                print(f"    - {component.display_name}: {component.description}")
        except Exception as e:
            print(f"  Error: {e}")

    # 3. Demonstrate framework integration
    print("\nFramework Integration:")
    integrator = get_framework_integrator()

    # Create a mock Langflow components dictionary
    mock_langflow_components = {
        "components": {"utilities": {"text_input": {"display_name": "Text Input", "description": "Basic text input"}}}
    }

    # Augment with framework components
    augmented_components = await integrator.augment_components_with_frameworks(mock_langflow_components)

    total_categories = len(augmented_components.get("components", {}))
    total_components = sum(len(comps) for comps in augmented_components.get("components", {}).values())
    print(f"  Total categories after integration: {total_categories}")
    print(f"  Total components after integration: {total_components}")

    # 4. Demonstrate execution enhancement
    print("\nExecution Enhancement:")
    enhancer = get_framework_execution_enhancer()

    # Mock component data for framework component
    framework_component_data = {
        "framework": "agno",
        "framework_component_id": "agno-text-tool",
        "template": {
            "framework": "agno",
            "display_name": "Agno Text Tool",
        },
    }

    # Mock execution context
    execution_context = {
        "inputs": {"text": "Hello, world!"},
        "config": {},
        "session_id": "test-session",
        "user_id": "test-user",
    }

    is_framework_component = enhancer.is_framework_component(framework_component_data)
    framework_type = enhancer.get_component_framework(framework_component_data)

    print(f"  Is framework component: {is_framework_component}")
    print(f"  Framework type: {framework_type}")

    if is_framework_component and framework_type:
        try:
            result = await enhancer.enhance_component_execution(framework_component_data, execution_context)
            print(f"  Execution result: {result}")
        except Exception as e:
            print(f"  Execution error: {e}")

    # 5. Show framework adaptation capabilities
    print("\nFramework Adapters:")
    for framework in [FrameworkType.LANGFLOW, FrameworkType.AGNO]:
        try:
            adapter = await manager.get_adapter(framework)
            print(f"  {framework.value} adapter: {adapter.__class__.__name__}")
            print(f"    Status: {'Available' if adapter else 'Not Available'}")
        except Exception as e:
            print(f"  {framework.value} adapter error: {e}")


def create_sample_flow_with_frameworks() -> dict[str, Any]:
    """Create a sample flow that demonstrates mixing Langflow and Agno components."""
    return {
        "name": "Mixed Framework Flow",
        "description": "A flow that uses both Langflow and Agno components",
        "nodes": [
            {
                "id": "input-1",
                "type": "langflow-text-input",
                "framework": "langflow",
                "data": {"template": {"display_name": "Text Input", "framework": "langflow"}},
                "position": {"x": 100, "y": 100},
            },
            {
                "id": "agno-tool-1",
                "type": "agno-text-processor",
                "framework": "agno",
                "data": {
                    "template": {"display_name": "Agno Text Processor", "framework": "agno"},
                    "framework_component_id": "agno-text-processor",
                },
                "position": {"x": 300, "y": 100},
            },
            {
                "id": "output-1",
                "type": "langflow-text-output",
                "framework": "langflow",
                "data": {"template": {"display_name": "Text Output", "framework": "langflow"}},
                "position": {"x": 500, "y": 100},
            },
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "input-1",
                "target": "agno-tool-1",
                "sourceHandle": "output",
                "targetHandle": "input",
            },
            {
                "id": "edge-2",
                "source": "agno-tool-1",
                "target": "output-1",
                "sourceHandle": "output",
                "targetHandle": "input",
            },
        ],
    }


async def main():
    """Main demonstration function."""
    await demonstrate_framework_system()

    print("\nSample Mixed Framework Flow:")
    print("=" * 50)
    sample_flow = create_sample_flow_with_frameworks()
    print(f"Flow: {sample_flow['name']}")
    print(f"Description: {sample_flow['description']}")
    print(f"Nodes: {len(sample_flow['nodes'])}")
    print(f"Edges: {len(sample_flow['edges'])}")

    # Show framework distribution
    frameworks = {}
    for node in sample_flow["nodes"]:
        framework = node.get("framework", "unknown")
        frameworks[framework] = frameworks.get(framework, 0) + 1

    print("\nFramework distribution:")
    for framework, count in frameworks.items():
        print(f"  {framework}: {count} components")


if __name__ == "__main__":
    asyncio.run(main())
