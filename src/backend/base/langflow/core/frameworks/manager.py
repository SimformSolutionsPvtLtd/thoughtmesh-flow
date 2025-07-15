"""Framework manager for coordinating multiple framework adapters."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from .base import FrameworkAdapter
from .exceptions import (
    ComponentNotFoundError,
    FrameworkNotInitializedError,
)
from .types import ComponentMetadata, ExecutionContext, ExecutionResult, FrameworkType

logger = logging.getLogger(__name__)


class FrameworkManager:
    """Manager for coordinating multiple framework adapters."""

    def __init__(self):
        self._adapters: dict[FrameworkType, FrameworkAdapter] = {}
        self._adapter_classes: dict[FrameworkType, type[FrameworkAdapter]] = {}
        self._default_framework = FrameworkType.LANGFLOW
        self._initialized = False

    def register_adapter(self, framework_type: FrameworkType, adapter_class: type[FrameworkAdapter]):
        """Register an adapter class for a framework type.

        Args:
            framework_type: The framework type
            adapter_class: The adapter class to register
        """
        self._adapter_classes[framework_type] = adapter_class
        logger.info("Registered adapter for %s", framework_type)

    async def initialize(
        self, framework_configs: dict[FrameworkType, dict[str, Any]] | None = None
    ) -> dict[FrameworkType, bool]:
        """Initialize all registered framework adapters.

        Args:
            framework_configs: Optional configurations for each framework

        Returns:
            Dict mapping framework types to initialization success status
        """
        if self._initialized:
            logger.warning("FrameworkManager already initialized")
            return {ft: adapter.is_initialized for ft, adapter in self._adapters.items()}

        framework_configs = framework_configs or {}
        initialization_results = {}

        # Initialize adapters in parallel
        async def init_adapter(framework_type: FrameworkType, adapter_class: type[FrameworkAdapter]):
            try:
                config = framework_configs.get(framework_type, {})
                adapter = adapter_class(config)
                success = await adapter.initialize()

                if success:
                    self._adapters[framework_type] = adapter
                    logger.info("Successfully initialized %s adapter", framework_type)
                else:
                    logger.error("Failed to initialize %s adapter", framework_type)

                return framework_type, success
            except Exception as e:
                logger.error("Error initializing %s adapter: %s", framework_type, str(e))
                return framework_type, False

        # Run initializations concurrently
        tasks = [init_adapter(ft, adapter_class) for ft, adapter_class in self._adapter_classes.items()]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error("Adapter initialization failed with exception: %s", result)
            else:
                framework_type, success = result
                initialization_results[framework_type] = success

        self._initialized = True
        logger.info("FrameworkManager initialized. Success: %s", initialization_results)
        return initialization_results

    async def shutdown(self):
        """Shutdown all framework adapters."""
        if not self._initialized:
            return

        shutdown_tasks = [adapter.shutdown() for adapter in self._adapters.values()]

        await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        self._adapters.clear()
        self._initialized = False
        logger.info("FrameworkManager shutdown complete")

    def get_adapter(self, framework_type: FrameworkType) -> FrameworkAdapter:
        """Get an adapter for a specific framework.

        Args:
            framework_type: The framework type

        Returns:
            The framework adapter

        Raises:
            FrameworkNotInitializedError: If framework not initialized
        """
        if not self._initialized:
            raise FrameworkNotInitializedError("FrameworkManager not initialized")

        adapter = self._adapters.get(framework_type)
        if not adapter:
            raise FrameworkNotInitializedError(f"Framework {framework_type} not available")

        return adapter

    def get_available_frameworks(self) -> list[FrameworkType]:
        """Get list of available (initialized) frameworks."""
        return list(self._adapters.keys())

    def set_default_framework(self, framework_type: FrameworkType):
        """Set the default framework."""
        if framework_type not in self._adapters:
            raise FrameworkNotInitializedError(f"Framework {framework_type} not available")
        self._default_framework = framework_type

    def get_default_framework(self) -> FrameworkType:
        """Get the default framework."""
        return self._default_framework

    async def get_all_components(self, framework_filter: FrameworkType | None = None) -> list[ComponentMetadata]:
        """Get all components from all frameworks.

        Args:
            framework_filter: Optional filter for specific framework

        Returns:
            List of all component metadata
        """
        if not self._initialized:
            raise FrameworkNotInitializedError("FrameworkManager not initialized")

        all_components = []
        frameworks_to_check = [framework_filter] if framework_filter else self._adapters.keys()

        for framework_type in frameworks_to_check:
            adapter = self._adapters.get(framework_type)
            if adapter:
                try:
                    components = await adapter.get_available_components()
                    all_components.extend(components)
                except Exception as e:
                    logger.error("Failed to get components from %s: %s", framework_type, str(e))

        return all_components

    async def get_component_metadata(self, component_id: str) -> ComponentMetadata | None:
        """Find component metadata across all frameworks.

        Args:
            component_id: Component identifier

        Returns:
            Component metadata or None if not found
        """
        for adapter in self._adapters.values():
            try:
                metadata = await adapter.get_component_metadata(component_id)
                if metadata:
                    return metadata
            except Exception as e:
                logger.error("Error getting component %s from %s: %s", component_id, adapter.framework_type, str(e))

        return None

    async def execute_component(self, component_id: str, context: ExecutionContext) -> ExecutionResult:
        """Execute a component using the appropriate framework.

        Args:
            component_id: Component identifier
            context: Execution context

        Returns:
            Execution result
        """
        # Determine framework from component ID
        framework_type = self._detect_framework_from_component(component_id)

        if framework_type not in self._adapters:
            raise ComponentNotFoundError(f"No adapter available for component {component_id}")

        adapter = self._adapters[framework_type]
        return await adapter.execute_component(context)

    def _detect_framework_from_component(self, component_id: str) -> FrameworkType:
        """Detect framework type from component ID."""
        if component_id.startswith("agno-"):
            return FrameworkType.AGNO
        return FrameworkType.LANGFLOW

    async def get_framework_status(self) -> dict[str, Any]:
        """Get status of all frameworks."""
        status = {"initialized": self._initialized, "default_framework": self._default_framework, "frameworks": {}}

        for framework_type, adapter in self._adapters.items():
            try:
                framework_info = await adapter.get_framework_info()
                status["frameworks"][framework_type] = framework_info
            except Exception as e:
                status["frameworks"][framework_type] = {"type": framework_type, "initialized": False, "error": str(e)}

        return status
