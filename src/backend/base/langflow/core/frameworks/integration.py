"""Integration layer for framework system with Langflow components."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from langflow.core.frameworks.exceptions import FrameworkError

if TYPE_CHECKING:
    from langflow.core.frameworks.types import ComponentMetadata, FrameworkType

from langflow.interface.components import component_cache

logger = logging.getLogger(__name__)


class FrameworkComponentIntegrator:
    """Integrates framework components with Langflow's component discovery system."""

    def __init__(self) -> None:
        """Initialize the framework component integrator."""
        self._framework_manager = None

    @property
    def framework_manager(self):
        """Lazy-loaded framework manager to avoid circular imports."""
        if self._framework_manager is None:
            from langflow.core.frameworks import get_framework_manager

            self._framework_manager = get_framework_manager()
        return self._framework_manager

    async def augment_components_with_frameworks(self, langflow_components: dict[str, Any]) -> dict[str, Any]:
        """Augment existing Langflow components with framework components.

        Args:
            langflow_components: The existing Langflow components dictionary

        Returns:
            Updated components dictionary with framework components included
        """
        if not langflow_components:
            langflow_components = {"components": {}}
        elif "components" not in langflow_components:
            langflow_components["components"] = {}

        # Add framework components to each available framework
        for framework in self.framework_manager.get_available_frameworks():
            try:
                await self._add_framework_components(langflow_components, framework)
            except FrameworkError as e:
                logger.warning("Failed to load components for framework %s: %s", framework, e)
                continue

        return langflow_components

    async def _add_framework_components(self, components_dict: dict[str, Any], framework: FrameworkType) -> None:
        """Add components from a specific framework to the components dictionary.

        Args:
            components_dict: The components dictionary to update
            framework: The framework to load components from
        """
        try:
            framework_components = await self.framework_manager.get_all_components(framework_filter=framework)

            for component in framework_components:
                category = self._map_category_to_langflow(component.category)

                # Ensure category exists
                if category not in components_dict["components"]:
                    components_dict["components"][category] = {}

                # Convert ComponentMetadata to Langflow component format
                component_dict = self._convert_component_metadata(component, framework)

                # Use a unique key that includes framework info
                component_key = f"{component.name}-{framework.value}"
                components_dict["components"][category][component_key] = component_dict

                logger.debug("Added %s component: %s in category %s", framework, component.name, category)

        except Exception as e:
            logger.exception("Error adding components for framework %s", framework)
            msg = f"Failed to add components for {framework}"
            raise FrameworkError(msg) from e

    def _map_category_to_langflow(self, category: Any) -> str:
        """Map framework categories to Langflow categories.

        Args:
            category: The framework component category

        Returns:
            The corresponding Langflow category name
        """
        # For now, use a simple mapping - this can be expanded
        category_mapping = {
            "AGENTS": "agents",
            "CHAINS": "chains",
            "EMBEDDINGS": "embeddings",
            "LLMS": "llms",
            "MEMORIES": "memories",
            "PROMPTS": "prompts",
            "TOOLS": "tools",
            "RETRIEVERS": "retrievers",
            "TEXT_SPLITTERS": "textsplitters",
            "TOOLKITS": "toolkits",
            "UTILITIES": "utilities",
            "VECTOR_STORES": "vectorstores",
            "CUSTOM": "custom_components",
            "DOCUMENT_LOADERS": "documentloaders",
            "OUTPUT_PARSERS": "outputparsers",
            "WRAPPERS": "wrappers",
        }

        category_str = category.value if hasattr(category, "value") else str(category)

        return category_mapping.get(category_str, "utilities")

    def _convert_component_metadata(self, metadata: ComponentMetadata, framework: FrameworkType) -> dict[str, Any]:
        """Convert ComponentMetadata to Langflow component dictionary format.

        Args:
            metadata: The component metadata to convert
            framework: The framework this component belongs to

        Returns:
            Dictionary in Langflow component format
        """
        return {
            "template": {
                "display_name": metadata.display_name,
                "description": metadata.description,
                "documentation": "",
                "icon": metadata.icon,
                "type": "Component",
                "base_classes": ["BaseComponent"],
                "_type": "CustomComponent",
                "framework": framework.value,
                "framework_version": metadata.version,
                "inputs": metadata.inputs,
                "outputs": metadata.outputs,
                "config": metadata.config_schema,
            },
            "display_name": metadata.display_name,
            "description": metadata.description,
            "documentation": "",
            "icon": metadata.icon,
            "is_component": True,
            "framework": framework.value,
            "framework_component_id": metadata.id,
            "lazy_loaded": False,  # Framework components are fully loaded
            # Additional metadata for framework components
            "template_code": "",  # Framework components don't have template code
            "field_config": {},
            "frozen": False,
            "custom_fields": {},
        }

    async def get_framework_component(self, framework: FrameworkType, component_id: str) -> ComponentMetadata | None:
        """Get a specific component from a framework.

        Args:
            framework: The framework to get the component from
            component_id: The ID of the component to get

        Returns:
            The component metadata if found, None otherwise
        """
        try:
            components = await self.framework_manager.get_all_components(framework_filter=framework)
            for component in components:
                if component_id in {component.id, component.name}:
                    return component
        except FrameworkError:
            logger.exception("Failed to get component %s from framework %s", component_id, framework)
        return None


# Global integrator instance
_integrator: FrameworkComponentIntegrator | None = None


def get_framework_integrator() -> FrameworkComponentIntegrator:
    """Get the global framework component integrator instance."""
    global _integrator  # noqa: PLW0603
    if _integrator is None:
        _integrator = FrameworkComponentIntegrator()
    return _integrator


async def integrate_framework_components() -> None:
    """Integrate framework components with the global component cache."""
    if component_cache.all_types_dict is None:
        logger.warning("Component cache is not initialized, skipping framework integration")
        return

    integrator = get_framework_integrator()
    try:
        component_cache.all_types_dict = await integrator.augment_components_with_frameworks(
            component_cache.all_types_dict
        )
        logger.info("Successfully integrated framework components with component cache")
    except FrameworkError:
        logger.exception("Failed to integrate framework components")
        # Don't raise the exception to avoid breaking existing functionality
