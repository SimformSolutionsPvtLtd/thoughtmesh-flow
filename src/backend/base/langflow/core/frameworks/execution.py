"""Enhanced execution system that supports framework-specific components."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from langflow.core.frameworks.types import ExecutionContext, ExecutionResult, FrameworkType

from langflow.core.frameworks.exceptions import FrameworkError

logger = logging.getLogger(__name__)


class FrameworkExecutionEnhancer:
    """Enhances Langflow's execution system to support framework components."""

    def __init__(self) -> None:
        """Initialize the framework execution enhancer."""
        self._framework_manager = None

    @property
    def framework_manager(self):
        """Lazy-loaded framework manager to avoid circular imports."""
        if self._framework_manager is None:
            from langflow.core.frameworks import get_framework_manager

            self._framework_manager = get_framework_manager()
        return self._framework_manager

    async def execute_framework_component(
        self, framework: FrameworkType, component_id: str, context: ExecutionContext
    ) -> ExecutionResult:
        """Execute a component from a specific framework.

        Args:
            framework: The framework the component belongs to
            component_id: The ID of the component to execute
            context: The execution context

        Returns:
            The execution result

        Raises:
            FrameworkError: If execution fails
        """
        try:
            adapter = await self.framework_manager.get_adapter(framework)
            return await adapter.execute_component(context)
        except Exception as e:
            msg = f"Failed to execute {framework} component {component_id}"
            logger.exception(msg)
            raise FrameworkError(msg) from e

    async def execute_framework_flow(
        self, framework: FrameworkType, flow_data: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ExecutionResult:
        """Execute a flow using a specific framework.

        Args:
            framework: The framework to use for execution
            flow_data: The flow data to execute
            context: Optional execution context

        Returns:
            The execution result

        Raises:
            FrameworkError: If execution fails
        """
        try:
            adapter = await self.framework_manager.get_adapter(framework)
            return await adapter.execute_flow(flow_data, context)
        except Exception as e:
            msg = f"Failed to execute flow with {framework}"
            logger.exception(msg)
            raise FrameworkError(msg) from e

    def is_framework_component(self, component_data: dict[str, Any]) -> bool:
        """Check if a component is a framework component.

        Args:
            component_data: The component data to check

        Returns:
            True if the component is from a framework, False otherwise
        """
        # Check if component has framework metadata
        return (
            "framework" in component_data
            or "framework_component_id" in component_data
            or component_data.get("template", {}).get("framework") is not None
        )

    def get_component_framework(self, component_data: dict[str, Any]) -> FrameworkType | None:
        """Get the framework type for a component.

        Args:
            component_data: The component data

        Returns:
            The framework type if found, None otherwise
        """
        # Try to get framework from different possible locations
        framework_str = component_data.get("framework") or component_data.get("template", {}).get("framework")

        if framework_str:
            try:
                from langflow.core.frameworks.types import FrameworkType  # noqa: PLC0415

                return FrameworkType(framework_str)
            except (ValueError, ImportError):
                logger.warning("Unknown framework type: %s", framework_str)

        return None

    async def enhance_component_execution(
        self, component_data: dict[str, Any], execution_context: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Enhance component execution with framework-specific logic.

        Args:
            component_data: The component data
            execution_context: The execution context

        Returns:
            Enhanced execution result if this is a framework component, None otherwise
        """
        if not self.is_framework_component(component_data):
            return None

        framework = self.get_component_framework(component_data)
        if not framework:
            return None

        try:
            # Create execution context for framework
            from langflow.core.frameworks.types import ExecutionContext  # noqa: PLC0415

            component_id = component_data.get("framework_component_id") or component_data.get("id", "unknown")

            context = ExecutionContext(
                component_id=component_id,
                inputs=execution_context.get("inputs", {}),
                config=execution_context.get("config", {}),
                session_id=execution_context.get("session_id"),
                user_id=execution_context.get("user_id"),
            )

            result = await self.execute_framework_component(framework, component_id, context)

        except FrameworkError:
            logger.exception("Framework component execution failed")
            return {
                "success": False,
                "data": None,
                "error": "Framework component execution failed",
                "execution_time": 0.0,
                "metadata": {},
            }
        else:
            # Convert ExecutionResult to Langflow format
            return {
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "execution_time": result.execution_time,
                "metadata": result.metadata,
            }


# Global enhancer instance
_enhancer: FrameworkExecutionEnhancer | None = None


def get_framework_execution_enhancer() -> FrameworkExecutionEnhancer:
    """Get the global framework execution enhancer instance."""
    global _enhancer  # noqa: PLW0603
    if _enhancer is None:
        _enhancer = FrameworkExecutionEnhancer()
    return _enhancer


async def enhance_component_execution(
    component_data: dict[str, Any], execution_context: dict[str, Any]
) -> dict[str, Any] | None:
    """Enhance component execution with framework support.

    This is a convenience function that can be called from existing execution code.

    Args:
        component_data: The component data
        execution_context: The execution context

    Returns:
        Enhanced execution result if this is a framework component, None otherwise
    """
    enhancer = get_framework_execution_enhancer()
    return await enhancer.enhance_component_execution(component_data, execution_context)
