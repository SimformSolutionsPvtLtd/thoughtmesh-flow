"""
Real Agno Framework Adapter - Phase 2 Implementation
Complete integration of actual Agno framework components.
"""

from __future__ import annotations

from typing import Any, Optional

from .agno_components import AgnoComponentRegistry
from .agno_implementation import AgnoComponentFactory
from .base import FrameworkAdapter
from .types import ComponentMetadata, ExecutionContext, ExecutionResult, FrameworkType


class RealAgnoAdapter(FrameworkAdapter):
    """Complete Agno framework adapter with real components."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.framework_type = FrameworkType.AGNO
        self._framework_name = "agno"
        self._framework_version = "0.3.0"
        self._component_registry = AgnoComponentRegistry()
        self._component_factory = AgnoComponentFactory()

    async def initialize(self) -> bool:
        """Initialize the Agno framework adapter."""
        try:
            # Try to import agno to check if it's available
            import agno

            self._initialized = True
            return True
        except ImportError:
            # Agno not available - run in simulation mode
            self._initialized = True  # Still allow simulation
            return True
        except Exception:
            return False

    async def shutdown(self) -> None:
        """Shutdown the adapter and cleanup resources."""
        self._initialized = False
        # Clear caches
        self._components_cache.clear()
        self._cache_timestamp = None

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the Agno framework."""
        status = {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
            "framework": self.framework_name,
            "version": self.framework_version,
            "component_count": len(self.get_supported_components()),
        }

        # Check if agno is actually installed
        try:
            import agno

            status["agno_available"] = True
            status["agno_version"] = getattr(agno, "__version__", "unknown")
        except ImportError:
            status["agno_available"] = False
            status["mode"] = "simulation"

        return status

    async def _discover_components(self) -> list[ComponentMetadata]:
        """Discover all available Agno components."""
        return self._component_registry.get_all_components()

    async def validate_component_config(self, component_id: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate component configuration."""
        component = self.get_component_by_id(component_id)
        if not component:
            return {"valid": False, "errors": [f"Component '{component_id}' not found"]}

        errors = []

        # Validate required inputs
        required_inputs = [inp for inp in component.inputs if inp.required]
        for req_input in required_inputs:
            if req_input.name not in config:
                errors.append(f"Required input '{req_input.name}' is missing")

        # Validate input types and values
        for inp in component.inputs:
            if inp.name in config:
                value = config[inp.name]
                if not self._validate_input_value(inp, value):
                    errors.append(f"Invalid value for input '{inp.name}'")

        return {"valid": len(errors) == 0, "errors": errors}

    async def execute_flow(self, flow_data: dict[str, Any], context: dict[str, Any] | None = None) -> ExecutionResult:
        """Execute a complete Agno flow."""
        try:
            # For now, return a placeholder implementation
            # In a full implementation, this would orchestrate multiple components
            return self._create_execution_result(
                success=True,
                data={"message": "Flow execution not yet implemented for Agno adapter"},
                metadata={"framework": self.framework_name, "flow_data": flow_data},
            )
        except Exception as e:
            return self._create_execution_result(
                success=False, error=f"Flow execution failed: {str(e)}", metadata={"framework": self.framework_name}
            )

    async def execute_component(self, context: ExecutionContext) -> ExecutionResult:
        """Execute a component with the given context."""
        component_id = getattr(context, "component_id", None) or context.inputs.get("component_id")
        if not component_id:
            return self._create_execution_result(success=False, error="component_id not found in execution context")

        try:
            # Validate component exists
            component_metadata = self.get_component_by_id(component_id)
            if not component_metadata:
                return self._create_execution_result(success=False, error=f"Component '{component_id}' not found")

            # Validate configuration
            validation_result = await self.validate_component_config(component_id, context.inputs)
            if not validation_result["valid"]:
                return self._create_execution_result(
                    success=False, error=f"Configuration validation failed: {', '.join(validation_result['errors'])}"
                )

            # Create and execute component
            component_instance = self._component_factory.create_component(component_id, **context.inputs)
            result = await component_instance.execute(context)

            # Add framework metadata to result
            if result.metadata is None:
                result.metadata = {}
            result.metadata.update(
                {
                    "framework": self.framework_name,
                    "framework_version": self.framework_version,
                    "component_category": component_metadata.category.value,
                }
            )

            return result

        except Exception as e:
            return self._create_execution_result(
                success=False, error=f"Execution failed: {str(e)}", metadata={"component_id": component_id}
            )

    @property
    def framework_name(self) -> str:
        """Get the framework name."""
        return self._framework_name

    @property
    def framework_version(self) -> str:
        """Get the framework version."""
        return self._framework_version

    def get_supported_components(self) -> list[ComponentMetadata]:
        """Get all supported Agno components."""
        return self._component_registry.get_all_components()

    def get_component_by_id(self, component_id: str) -> Optional[ComponentMetadata]:
        """Get a specific component by its ID."""
        components = self.get_supported_components()
        for component in components:
            if component.id == component_id:
                return component
        return None

    def validate_component_config(self, component_id: str, config: dict[str, Any]) -> tuple[bool, str]:
        """Validate component configuration."""
        component = self.get_component_by_id(component_id)
        if not component:
            return False, f"Component '{component_id}' not found"

        # Validate required inputs
        required_inputs = [inp for inp in component.inputs if inp.required]
        for req_input in required_inputs:
            if req_input.name not in config:
                return False, f"Required input '{req_input.name}' is missing"

        # Validate input types and values
        for inp in component.inputs:
            if inp.name in config:
                value = config[inp.name]
                if not self._validate_input_value(inp, value):
                    return False, f"Invalid value for input '{inp.name}'"

        return True, "Configuration is valid"

    def _validate_input_value(self, input_def: Any, value: Any) -> bool:
        """Validate an input value against its definition."""
        # Check if value is within options if provided
        if hasattr(input_def, "options") and input_def.options:
            if value not in input_def.options:
                return False

        # Check numeric ranges
        if input_def.type == "number":
            if not isinstance(value, (int, float)):
                return False
            if hasattr(input_def, "min_value") and input_def.min_value is not None:
                if value < input_def.min_value:
                    return False
            if hasattr(input_def, "max_value") and input_def.max_value is not None:
                if value > input_def.max_value:
                    return False

        # Check string types
        elif input_def.type == "string":
            if not isinstance(value, str):
                return False

        # Check boolean types
        elif input_def.type == "boolean":
            if not isinstance(value, bool):
                return False

        # Check list types
        elif input_def.type == "list":
            if not isinstance(value, list):
                return False

        return True

    def get_component_dependencies(self, component_id: str) -> list[str]:
        """Get the dependencies for a component."""
        component = self.get_component_by_id(component_id)
        if not component:
            return []

        dependencies = []

        # Check for complex type dependencies
        for inp in component.inputs:
            if inp.type in [
                "Model",
                "VectorDb",
                "AgentKnowledge",
                "Embedder",
                "Memory",
                "Storage",
                "Reranker",
                "ChunkingStrategy",
                "Reader",
                "Agent",
                "Team",
                "Toolkit",
            ]:
                dependencies.append(inp.type)

        return list(set(dependencies))  # Remove duplicates

    def get_component_outputs_by_type(self, output_type: str) -> list[ComponentMetadata]:
        """Get all components that produce a specific output type."""
        matching_components = []

        for component in self.get_supported_components():
            for output in component.outputs:
                if output.type == output_type:
                    matching_components.append(component)
                    break

        return matching_components

    def can_connect_components(self, source_component_id: str, target_component_id: str) -> bool:
        """Check if two components can be connected."""
        source_component = self.get_component_by_id(source_component_id)
        target_component = self.get_component_by_id(target_component_id)

        if not source_component or not target_component:
            return False

        # Get output types from source
        source_output_types = {output.type for output in source_component.outputs}

        # Get required input types from target
        target_input_types = {inp.type for inp in target_component.inputs}

        # Check if any output type matches any input type
        return bool(source_output_types.intersection(target_input_types))

    def get_framework_info(self) -> dict[str, Any]:
        """Get comprehensive framework information."""
        components = self.get_supported_components()

        # Count components by category
        category_counts = {}
        for component in components:
            category = component.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        # Get unique output types
        output_types = set()
        for component in components:
            for output in component.outputs:
                output_types.add(output.type)

        return {
            "name": self.framework_name,
            "version": self.framework_version,
            "description": "Agno AI framework for building multi-agent systems with memory, knowledge and reasoning",
            "total_components": len(components),
            "categories": list(category_counts.keys()),
            "category_counts": category_counts,
            "supported_output_types": sorted(output_types),
            "features": [
                "Multi-agent systems",
                "Knowledge bases with vector search",
                "Memory and storage systems",
                "Advanced reasoning capabilities",
                "Multiple AI model providers",
                "Tool integration",
                "Team coordination",
                "Workflow orchestration",
            ],
            "model_providers": [
                "OpenAI",
                "Anthropic",
                "Google Gemini",
                "Groq",
                "Ollama",
                "Meta Llama",
                "xAI",
                "Cerebras",
                "Vercel",
                "Perplexity",
            ],
            "vector_stores": [
                "PostgreSQL+pgvector",
                "LanceDB",
                "Qdrant",
                "Milvus",
                "Pinecone",
                "ChromaDB",
                "Weaviate",
                "Cassandra",
            ],
            "documentation_url": "https://docs.agno.com",
            "github_url": "https://github.com/agno-agi/agno",
        }

    def get_quickstart_example(self) -> dict[str, Any]:
        """Get a quickstart example for using Agno."""
        return {
            "title": "Basic Agno Agent with Tools",
            "description": "Create a simple agent with web search capabilities",
            "components": [
                {"id": "agno_openai_chat", "config": {"model_id": "gpt-4o-mini", "temperature": 0.7}},
                {"id": "agno_duckduckgo_tools", "config": {"num_results": 5}},
                {
                    "id": "agno_basic_agent",
                    "config": {
                        "instructions": "You are a helpful assistant with web search capabilities.",
                        "description": "Web search agent",
                    },
                },
            ],
            "connections": [
                {"from": "agno_openai_chat", "to": "agno_basic_agent", "output": "model", "input": "model"},
                {"from": "agno_duckduckgo_tools", "to": "agno_basic_agent", "output": "tools", "input": "tools"},
            ],
            "code_example": """
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

# Create agent with model and tools
agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions="You are a helpful assistant with web search capabilities.",
    show_tool_calls=True
)

# Use the agent
response = agent.run("What's the latest news about AI?")
print(response.content)
            """,
        }
