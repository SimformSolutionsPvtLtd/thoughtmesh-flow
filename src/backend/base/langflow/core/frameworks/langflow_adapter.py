"""Langflow framework adapter for backward compatibility."""

from __future__ import annotations

import time
from typing import Any

from .base import FrameworkAdapter
from .exceptions import ComponentExecutionError
from .types import (
    ComponentCategory,
    ComponentMetadata,
    ExecutionContext,
    ExecutionResult,
    FrameworkType,
    InputDefinition,
    OutputDefinition,
)


class LangflowAdapter(FrameworkAdapter):
    """Adapter for existing Langflow components."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.framework_type = FrameworkType.LANGFLOW

    async def initialize(self) -> bool:
        """Initialize Langflow adapter."""
        try:
            # Langflow is always available in this context
            self._initialized = True
            return True
        except Exception:
            return False

    async def shutdown(self) -> None:
        """Cleanup Langflow adapter."""
        self._initialized = False

    async def health_check(self) -> dict[str, Any]:
        """Perform health check."""
        return {"status": "healthy" if self._initialized else "unhealthy", "timestamp": time.time()}

    async def _discover_components(self) -> list[ComponentMetadata]:
        """Discover existing Langflow components."""
        # Import existing Langflow components
        try:
            from langflow.interface.components import get_and_cache_all_types_dict
            from langflow.services.deps import get_settings_service

            # Get all component types
            settings_service = get_settings_service()
            await get_and_cache_all_types_dict(settings_service)

            # For now, return a placeholder list
            # This would need to be implemented based on actual Langflow component discovery
            components = []

            # Create basic Langflow component placeholders
            basic_components = [
                {
                    "id": "langflow-text-input",
                    "name": "TextInput",
                    "display_name": "Text Input",
                    "description": "Basic text input component",
                    "category": ComponentCategory.UTILITIES,
                    "icon": "type",
                },
                {
                    "id": "langflow-text-output",
                    "name": "TextOutput",
                    "display_name": "Text Output",
                    "description": "Basic text output component",
                    "category": ComponentCategory.UTILITIES,
                    "icon": "type",
                },
            ]

            for comp_data in basic_components:
                metadata = ComponentMetadata(
                    id=comp_data["id"],
                    name=comp_data["name"],
                    display_name=comp_data["display_name"],
                    description=comp_data["description"],
                    category=comp_data["category"],
                    framework=FrameworkType.LANGFLOW,
                    version="1.0.0",
                    icon=comp_data["icon"],
                    inputs=[],
                    outputs=[],
                    config_schema={},
                )
                components.append(metadata)

            return components

        except Exception:
            # If we can't discover components, return empty list
            return []

    def _create_component_metadata(self, component_class) -> ComponentMetadata:
        """Create metadata from existing Langflow component."""
        # Extract information from component class
        display_name = getattr(component_class, "display_name", component_class.__name__)
        description = getattr(component_class, "description", "")
        icon = getattr(component_class, "icon", None)

        # Map to our category system
        category = self._map_component_category(component_class)

        # Extract inputs and outputs if available
        inputs = self._extract_component_inputs(component_class)
        outputs = self._extract_component_outputs(component_class)

        return ComponentMetadata(
            id=f"langflow-{component_class.__name__.lower()}",
            name=component_class.__name__,
            display_name=display_name,
            description=description,
            category=category,
            framework=FrameworkType.LANGFLOW,
            version="1.0.0",
            icon=icon,
            inputs=inputs,
            outputs=outputs,
            config_schema={},
        )

    def _map_component_category(self, component_class) -> ComponentCategory:
        """Map component class to category."""
        class_name = component_class.__name__.lower()
        module_name = component_class.__module__.lower()

        if "tool" in class_name or "tools" in module_name:
            return ComponentCategory.TOOLS
        elif "model" in class_name or "models" in module_name:
            return ComponentCategory.MODELS
        elif "vector" in class_name or "vectorstore" in module_name:
            return ComponentCategory.VECTOR_STORES
        elif "embedding" in class_name or "embeddings" in module_name:
            return ComponentCategory.EMBEDDINGS
        elif "memory" in class_name or "memory" in module_name:
            return ComponentCategory.MEMORY
        elif "chain" in class_name or "chains" in module_name:
            return ComponentCategory.CHAINS
        elif "agent" in class_name or "agents" in module_name:
            return ComponentCategory.AGENTS
        else:
            return ComponentCategory.UTILITIES

    def _extract_component_inputs(self, component_class) -> list[InputDefinition]:
        """Extract input definitions from component."""
        inputs = []
        # This would need to be implemented based on how Langflow components define inputs
        # For now, return empty list
        return inputs

    def _extract_component_outputs(self, component_class) -> list[OutputDefinition]:
        """Extract output definitions from component."""
        outputs = []
        # This would need to be implemented based on how Langflow components define outputs
        # For now, return empty list
        return outputs

    async def validate_component_config(self, component_id: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate component configuration."""
        # For Langflow components, we can use existing validation logic
        return {"valid": True, "errors": []}

    async def execute_component(self, context: ExecutionContext) -> ExecutionResult:
        """Execute a Langflow component."""
        start_time = time.time()

        try:
            # This would integrate with existing Langflow execution logic
            # For now, return a placeholder result
            result_data = f"Executed Langflow component {context.component_id}"

            execution_time = time.time() - start_time

            return self._create_execution_result(
                success=True,
                data=result_data,
                execution_time=execution_time,
                metadata={"component_id": context.component_id},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_execution_result(
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={"component_id": context.component_id},
            )

    async def execute_flow(self, flow_data: dict[str, Any], context: dict[str, Any] | None = None) -> ExecutionResult:
        """Execute a Langflow flow."""
        start_time = time.time()

        try:
            # This would integrate with existing Langflow flow execution
            # For now, return a placeholder result
            result_data = "Executed Langflow flow"

            execution_time = time.time() - start_time

            return self._create_execution_result(
                success=True, data=result_data, execution_time=execution_time, metadata={"flow_id": flow_data.get("id")}
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return self._create_execution_result(
                success=False, error=str(e), execution_time=execution_time, metadata={"flow_id": flow_data.get("id")}
            )
