"""Integration test for framework manager adapter selection."""

import asyncio
import logging
from typing import Any

from langflow.core.frameworks import (
    FrameworkType,
    get_framework_manager,
)

# Set up logging to see adapter selection
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_framework_manager_integration():
    """Test that the framework manager properly initializes with available adapters."""
    logger.info("Testing Framework Manager Integration")
    logger.info("=" * 50)

    # Get the global framework manager
    manager = get_framework_manager()
    logger.info("Framework manager created")

    # Initialize the manager
    logger.info("Initializing framework adapters...")
    init_results = await manager.initialize()

    logger.info("Initialization results:")
    for framework_type, success in init_results.items():
        logger.info("  %s: %s", framework_type, "✓" if success else "✗")

    # Check available frameworks
    available = manager.get_available_frameworks()
    logger.info("Available frameworks: %s", available)

    # Test framework status
    status = await manager.get_framework_status()
    logger.info("Framework status:")
    logger.info("  Initialized: %s", status["initialized"])
    logger.info("  Default: %s", status["default_framework"])

    for framework_name, framework_info in status["frameworks"].items():
        logger.info("  %s:", framework_name)
        logger.info("    Type: %s", framework_info.get("type"))
        logger.info("    Initialized: %s", framework_info.get("initialized"))
        if "error" in framework_info:
            logger.info("    Error: %s", framework_info["error"])

    # Test getting adapters
    for framework_type in [FrameworkType.LANGFLOW, FrameworkType.AGNO]:
        try:
            adapter = manager.get_adapter(framework_type)
            logger.info("Got %s adapter: %s", framework_type, adapter.__class__.__name__)

            # Test adapter functionality
            if adapter.is_initialized:
                framework_info = await adapter.get_framework_info()
                logger.info("  Framework info: %s", framework_info)

                # Test component discovery
                components = await adapter.get_available_components()
                logger.info("  Found %d components", len(components))

                # Show first few components
                for comp in components[:3]:
                    logger.info("    - %s: %s", comp.display_name, comp.description)
        except Exception as e:
            logger.error("Error testing %s adapter: %s", framework_type, str(e))

    logger.info("Integration test completed!")


async def test_agno_adapter_type():
    """Test which Agno adapter was selected."""
    logger.info("\nTesting Agno Adapter Selection")
    logger.info("-" * 30)

    manager = get_framework_manager()

    # Initialize if needed
    if not manager._initialized:
        await manager.initialize()

    try:
        agno_adapter = manager.get_adapter(FrameworkType.AGNO)
        adapter_class = agno_adapter.__class__.__name__

        logger.info("Selected Agno adapter: %s", adapter_class)

        if adapter_class == "AgnoAdapterReal":
            logger.info("✓ Using real Agno adapter with actual API")
        elif adapter_class == "AgnoFrameworkAdapter":
            logger.info("i Using simulated Agno adapter (Agno not installed)")
        else:
            logger.warning("? Unknown Agno adapter type: %s", adapter_class)

    except Exception as e:
        logger.error("Failed to get Agno adapter: %s", str(e))


if __name__ == "__main__":

    async def main():
        await test_framework_manager_integration()
        await test_agno_adapter_type()

    asyncio.run(main())
