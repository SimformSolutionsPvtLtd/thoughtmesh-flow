#!/usr/bin/env python3

import asyncio
import logging
import sys
from pathlib import Path

# Add the backend to the path
backend_path = Path(__file__).parent / "src" / "backend" / "base"
sys.path.insert(0, str(backend_path))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_framework_manager():
    """Test framework manager initialization in isolation."""
    try:
        logger.info("Starting framework manager test...")
        
        # Import framework manager
        from langflow.core.frameworks import get_framework_manager
        
        logger.info("Getting framework manager...")
        manager = get_framework_manager()
        
        logger.info("Framework manager created, checking adapters...")
        logger.info(f"Available adapters: {list(manager._adapter_classes.keys())}")
        
        logger.info("Initializing framework manager...")
        results = await manager.initialize()
        
        logger.info(f"Initialization results: {results}")
        
        logger.info("Testing get_available_frameworks...")
        frameworks = manager.get_available_frameworks()
        logger.info(f"Available frameworks: {frameworks}")
        
        logger.info("Testing get_all_components for agno...")
        components = await manager.get_all_components(framework_filter="agno")
        logger.info(f"Got {len(components)} agno components")
        
        if components:
            first_comp = components[0]
            logger.info(f"First component: {first_comp.name} ({first_comp.display_name})")
        
        logger.info("✓ Framework manager test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Framework manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    success = await test_framework_manager()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
