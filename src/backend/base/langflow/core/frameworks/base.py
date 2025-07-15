"""Base framework adapter for the Langflow framework abstraction layer."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from .types import (
    ComponentMetadata,
    ExecutionContext,
    ExecutionResult,
    FrameworkType,
)

logger = logging.getLogger(__name__)


class FrameworkAdapter(ABC):
    """Abstract base class for framework adapters."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.framework_type: FrameworkType
        self.client: Any = None
        self.config = config or {}
        self._initialized = False
        self._components_cache: dict[str, ComponentMetadata] = {}
        self._cache_timestamp: float | None = None
        self._cache_ttl = 300  # 5 minutes cache TTL

    @property
    def is_initialized(self) -> bool:
        """Check if adapter is initialized."""
        return self._initialized

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the framework client.

        Returns:
            bool: True if initialization successful, False otherwise
        """

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup resources when shutting down."""

    @abstractmethod
    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the framework.

        Returns:
            Dict containing health status information
        """

    @abstractmethod
    async def _discover_components(self) -> list[ComponentMetadata]:
        """Discover all available components from the framework.

        Returns:
            List of component metadata
        """

    async def get_available_components(self, *, force_refresh: bool = False) -> list[ComponentMetadata]:
        """Get all available components with caching.

        Args:
            force_refresh: Force refresh of component cache

        Returns:
            List of component metadata
        """
        if not self._initialized:
            msg = f"{self.framework_type} adapter not initialized"
            raise RuntimeError(msg)

        current_time = time.time()
        cache_expired = self._cache_timestamp is None or (current_time - self._cache_timestamp) > self._cache_ttl

        if force_refresh or cache_expired or not self._components_cache:
            logger.info("Refreshing component cache for %s", self.framework_type)
            components = await self._discover_components()

            # Update cache
            self._components_cache = {comp.id: comp for comp in components}
            self._cache_timestamp = current_time

            logger.info("Cached %d components for %s", len(components), self.framework_type)

        return list(self._components_cache.values())

    async def get_component_metadata(self, component_id: str) -> ComponentMetadata | None:
        """Get metadata for a specific component.

        Args:
            component_id: Component identifier

        Returns:
            Component metadata or None if not found
        """
        await self.get_available_components()
        return self._components_cache.get(component_id)

    @abstractmethod
    async def validate_component_config(self, component_id: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate component configuration.

        Args:
            component_id: Component identifier
            config: Configuration to validate

        Returns:
            Dict with validation results: {"valid": bool, "errors": list[str]}
        """

    @abstractmethod
    async def execute_component(self, context: ExecutionContext) -> ExecutionResult:
        """Execute a single component.

        Args:
            context: Execution context with inputs, config, etc.

        Returns:
            Execution result
        """

    @abstractmethod
    async def execute_flow(self, flow_data: dict[str, Any], context: dict[str, Any] | None = None) -> ExecutionResult:
        """Execute a complete flow.

        Args:
            flow_data: Flow definition
            context: Optional execution context

        Returns:
            Execution result
        """

    async def get_framework_info(self) -> dict[str, Any]:
        """Get information about this framework.

        Returns:
            Dict with framework information
        """
        components = await self.get_available_components()
        health = await self.health_check()

        return {
            "type": self.framework_type,
            "name": self.framework_type.value.title(),
            "initialized": self._initialized,
            "component_count": len(components),
            "health": health,
            "cache_timestamp": self._cache_timestamp,
            "config": self.config,
        }

    def _create_execution_result(
        self,
        *,
        success: bool,
        data: Any = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
        execution_time: float | None = None,
    ) -> ExecutionResult:
        """Helper method to create execution results."""
        return ExecutionResult(
            success=success,
            data=data,
            error=error,
            metadata=metadata or {},
            execution_time=execution_time,
            framework=self.framework_type,
        )
