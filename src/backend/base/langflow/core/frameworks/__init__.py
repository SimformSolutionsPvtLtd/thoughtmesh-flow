"""Framework abstraction layer for Langflow."""

import logging

from langflow.core.frameworks.base import FrameworkAdapter
from langflow.core.frameworks.exceptions import (
    ComponentDiscoveryError,
    ComponentExecutionError,
    ComponentNotFoundError,
    ConfigurationValidationError,
    FlowExecutionError,
    FrameworkError,
    FrameworkInitializationError,
    FrameworkNotInitializedError,
)
from langflow.core.frameworks.execution import FrameworkExecutionEnhancer, get_framework_execution_enhancer
from langflow.core.frameworks.integration import FrameworkComponentIntegrator, get_framework_integrator
from langflow.core.frameworks.langflow_adapter import LangflowAdapter
from langflow.core.frameworks.manager import FrameworkManager
from langflow.core.frameworks.types import (
    ComponentCategory,
    ComponentMetadata,
    ExecutionContext,
    ExecutionResult,
    FrameworkType,
    InputDefinition,
    OutputDefinition,
)

logger = logging.getLogger(__name__)

# Try to import the real Agno adapter first, fall back to simulated
AgnoAdapter: type[FrameworkAdapter]
try:
    from langflow.core.frameworks.agno_adapter_real import AgnoAdapterReal

    AgnoAdapter = AgnoAdapterReal
    logger.info("Using real Agno adapter")
except ImportError as e:
    logger.info("Real Agno adapter not available (%s), falling back to simulated", str(e))
    from langflow.core.frameworks.agno_adapter import AgnoFrameworkAdapter

    AgnoAdapter = AgnoFrameworkAdapter


def create_framework_manager() -> FrameworkManager:
    """Create and configure a framework manager with all available adapters.

    Returns:
        Configured FrameworkManager instance
    """
    manager = FrameworkManager()

    # Register Langflow adapter (always available)
    manager.register_adapter(FrameworkType.LANGFLOW, LangflowAdapter)

    # Register Agno adapter (real or simulated)
    manager.register_adapter(FrameworkType.AGNO, AgnoAdapter)

    logger.info(
        "Framework manager created with adapters: Langflow, Agno (%s)",
        "real" if AgnoAdapter.__name__ == "AgnoAdapterReal" else "simulated",
    )

    return manager


# Global framework manager instance
_framework_manager: FrameworkManager | None = None


def get_framework_manager() -> FrameworkManager:
    """Get or create the global framework manager instance.

    Returns:
        Global FrameworkManager instance
    """
    # Use a simple module-level variable without global statement
    # This is a common pattern for singletons in Python
    if "_framework_manager" not in globals() or globals()["_framework_manager"] is None:
        globals()["_framework_manager"] = create_framework_manager()
    return globals()["_framework_manager"]


__all__ = [
    "AgnoAdapter",
    "ComponentCategory",
    "ComponentDiscoveryError",
    "ComponentExecutionError",
    "ComponentMetadata",
    "ComponentNotFoundError",
    "ConfigurationValidationError",
    "ExecutionContext",
    "ExecutionResult",
    "FlowExecutionError",
    "FrameworkAdapter",
    "FrameworkComponentIntegrator",
    "FrameworkError",
    "FrameworkExecutionEnhancer",
    "FrameworkInitializationError",
    "FrameworkManager",
    "FrameworkNotInitializedError",
    "FrameworkType",
    "InputDefinition",
    "LangflowAdapter",
    "OutputDefinition",
    "create_framework_manager",
    "get_framework_execution_enhancer",
    "get_framework_integrator",
    "get_framework_manager",
]
