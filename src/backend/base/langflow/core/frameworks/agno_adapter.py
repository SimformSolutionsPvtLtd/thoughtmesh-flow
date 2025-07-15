"""Agno framework adapter for integrating Agno framework with Langflow."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from .base import FrameworkAdapter
from .exceptions import (
    ComponentExecutionError,
    ComponentNotFoundError,
    ConfigurationValidationError,
    FrameworkInitializationError,
)
from .types import (
    ComponentCategory,
    ComponentMetadata,
    ExecutionContext,
    ExecutionResult,
    FrameworkType,
    InputDefinition,
    OutputDefinition,
)

logger = logging.getLogger(__name__)


class AgnoFrameworkAdapter(FrameworkAdapter):
    """Adapter for Agno framework integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.framework_type = FrameworkType.AGNO
        self._agno_version: str | None = None
        self._connection_pool = None

    async def initialize(self) -> bool:
        """Initialize Agno client."""
        try:
            # Import Agno framework
            try:
                # For now, we'll simulate Agno import since it's not available
                # In real implementation, this would be: import agno
                # self._agno_version = getattr(agno, '__version__', 'unknown')
                logger.info("Simulating Agno framework import")
                self._agno_version = "1.0.0"  # Simulated version
            except ImportError:
                logger.error("Agno framework not installed. Install with: pip install agno")
                return False

            # Initialize client with configuration
            client_config = self._prepare_client_config()
            # self.client = agno.Client(**client_config)
            # Simulated client
            self.client = SimulatedAgnoClient(**client_config)

            # Test connection
            # await self.client.initialize()
            await self.client.initialize()

            # Verify connection
            health_status = await self.health_check()
            if health_status.get("status") != "healthy":
                logger.error("Agno health check failed after initialization")
                return False

            self._initialized = True
            logger.info("Agno framework adapter initialized successfully")
            return True

        except Exception as e:
            logger.error("Failed to initialize Agno adapter: %s", str(e))
            self._initialized = False
            return False

    def _prepare_client_config(self) -> dict[str, Any]:
        """Prepare configuration for Agno client."""
        default_config = {
            "timeout": 30,
            "max_retries": 3,
            "connection_pool_size": 10,
        }

        # Override with user-provided config
        client_config = {**default_config, **self.config}

        # Handle API keys and authentication
        if "api_key" in self.config:
            client_config["api_key"] = self.config["api_key"]

        if "base_url" in self.config:
            client_config["base_url"] = self.config["base_url"]

        return client_config

    async def shutdown(self) -> None:
        """Cleanup Agno adapter resources."""
        try:
            if self.client:
                await self.client.close()

            if self._connection_pool:
                await self._connection_pool.close()

            self._initialized = False
            logger.info("Agno adapter shutdown complete")

        except Exception as e:
            logger.error("Error during Agno adapter shutdown: %s", str(e))

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on Agno framework."""
        try:
            if not self.client:
                return {"status": "unhealthy", "error": "Client not initialized"}

            # Ping Agno service
            ping_result = await self.client.ping()

            # Get service status
            status_info = await self.client.get_status()

            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": self._agno_version,
                "ping_time": ping_result.get("response_time"),
                "service_info": status_info,
            }

        except Exception as e:
            return {"status": "unhealthy", "timestamp": time.time(), "error": str(e)}

    async def _discover_components(self) -> list[ComponentMetadata]:
        """Discover all available Agno components."""
        if not self.client:
            raise FrameworkInitializationError("Agno client not initialized")

        components = []

        try:
            # Discover components in parallel
            discovery_tasks = [
                self._discover_tools(),
                self._discover_models(),
                self._discover_vector_stores(),
                self._discover_knowledge_bases(),
                self._discover_embeddings(),
                self._discover_retrievers(),
            ]

            results = await asyncio.gather(*discovery_tasks, return_exceptions=True)

            # Flatten results and handle exceptions
            for result in results:
                if isinstance(result, Exception):
                    logger.error("Component discovery failed: %s", result)
                else:
                    components.extend(result)

            logger.info("Discovered %d Agno components", len(components))
            return components

        except Exception as e:
            logger.error("Failed to discover Agno components: %s", str(e))
            return []

    async def _discover_tools(self) -> list[ComponentMetadata]:
        """Discover Agno tools."""
        try:
            tools = await self.client.tools.list()
            components = []

            for tool in tools:
                metadata = ComponentMetadata(
                    id=f"agno-tool-{tool.id}",
                    name=tool.name,
                    display_name=tool.display_name or tool.name,
                    description=tool.description or "",
                    category=ComponentCategory.TOOLS,
                    framework=FrameworkType.AGNO,
                    version=tool.version or "1.0.0",
                    icon="tool",
                    inputs=self._convert_agno_inputs(tool.inputs),
                    outputs=self._convert_agno_outputs(tool.outputs),
                    config_schema=tool.config_schema or {},
                    tags=tool.tags or [],
                    documentation_url=tool.documentation_url,
                )
                components.append(metadata)

            return components

        except Exception as e:
            logger.error("Failed to discover Agno tools: %s", str(e))
            return []

    async def _discover_models(self) -> list[ComponentMetadata]:
        """Discover Agno models."""
        try:
            models = await self.client.models.list()
            components = []

            for model in models:
                metadata = ComponentMetadata(
                    id=f"agno-model-{model.id}",
                    name=model.name,
                    display_name=model.display_name or model.name,
                    description=model.description or "",
                    category=ComponentCategory.MODELS,
                    framework=FrameworkType.AGNO,
                    version=model.version or "1.0.0",
                    icon="brain",
                    inputs=self._convert_agno_inputs(model.inputs),
                    outputs=self._convert_agno_outputs(model.outputs),
                    config_schema=model.config_schema or {},
                    tags=model.tags or [],
                    documentation_url=model.documentation_url,
                )
                components.append(metadata)

            return components

        except Exception as e:
            logger.error("Failed to discover Agno models: %s", str(e))
            return []

    async def _discover_vector_stores(self) -> list[ComponentMetadata]:
        """Discover Agno vector stores."""
        try:
            vector_stores = await self.client.vector_stores.list()
            components = []

            for vs in vector_stores:
                metadata = ComponentMetadata(
                    id=f"agno-vectorstore-{vs.id}",
                    name=vs.name,
                    display_name=vs.display_name or vs.name,
                    description=vs.description or "",
                    category=ComponentCategory.VECTOR_STORES,
                    framework=FrameworkType.AGNO,
                    version=vs.version or "1.0.0",
                    icon="database",
                    inputs=self._convert_agno_inputs(vs.inputs),
                    outputs=self._convert_agno_outputs(vs.outputs),
                    config_schema=vs.config_schema or {},
                    tags=vs.tags or [],
                    documentation_url=vs.documentation_url,
                )
                components.append(metadata)

            return components

        except Exception as e:
            logger.error("Failed to discover Agno vector stores: %s", str(e))
            return []

    async def _discover_knowledge_bases(self) -> list[ComponentMetadata]:
        """Discover Agno knowledge bases."""
        try:
            knowledge_bases = await self.client.knowledge_bases.list()
            components = []

            for kb in knowledge_bases:
                metadata = ComponentMetadata(
                    id=f"agno-kb-{kb.id}",
                    name=kb.name,
                    display_name=kb.display_name or kb.name,
                    description=kb.description or "",
                    category=ComponentCategory.KNOWLEDGE_BASES,
                    framework=FrameworkType.AGNO,
                    version=kb.version or "1.0.0",
                    icon="book",
                    inputs=self._convert_agno_inputs(kb.inputs),
                    outputs=self._convert_agno_outputs(kb.outputs),
                    config_schema=kb.config_schema or {},
                    tags=kb.tags or [],
                    documentation_url=kb.documentation_url,
                )
                components.append(metadata)

            return components

        except Exception as e:
            logger.error("Failed to discover Agno knowledge bases: %s", str(e))
            return []

    async def _discover_embeddings(self) -> list[ComponentMetadata]:
        """Discover Agno embedding models."""
        try:
            embeddings = await self.client.embeddings.list()
            components = []

            for embedding in embeddings:
                metadata = ComponentMetadata(
                    id=f"agno-embedding-{embedding.id}",
                    name=embedding.name,
                    display_name=embedding.display_name or embedding.name,
                    description=embedding.description or "",
                    category=ComponentCategory.EMBEDDINGS,
                    framework=FrameworkType.AGNO,
                    version=embedding.version or "1.0.0",
                    icon="vector",
                    inputs=self._convert_agno_inputs(embedding.inputs),
                    outputs=self._convert_agno_outputs(embedding.outputs),
                    config_schema=embedding.config_schema or {},
                    tags=embedding.tags or [],
                    documentation_url=embedding.documentation_url,
                )
                components.append(metadata)

            return components

        except Exception as e:
            logger.error("Failed to discover Agno embeddings: %s", str(e))
            return []

    async def _discover_retrievers(self) -> list[ComponentMetadata]:
        """Discover Agno retrievers."""
        try:
            retrievers = await self.client.retrievers.list()
            components = []

            for retriever in retrievers:
                metadata = ComponentMetadata(
                    id=f"agno-retriever-{retriever.id}",
                    name=retriever.name,
                    display_name=retriever.display_name or retriever.name,
                    description=retriever.description or "",
                    category=ComponentCategory.RETRIEVERS,
                    framework=FrameworkType.AGNO,
                    version=retriever.version or "1.0.0",
                    icon="search",
                    inputs=self._convert_agno_inputs(retriever.inputs),
                    outputs=self._convert_agno_outputs(retriever.outputs),
                    config_schema=retriever.config_schema or {},
                    tags=retriever.tags or [],
                    documentation_url=retriever.documentation_url,
                )
                components.append(metadata)

            return components

        except Exception as e:
            logger.error("Failed to discover Agno retrievers: %s", str(e))
            return []

    def _convert_agno_inputs(self, agno_inputs: list[Any] | None) -> list[InputDefinition]:
        """Convert Agno input definitions to our format."""
        if not agno_inputs:
            return []

        converted = []
        for inp in agno_inputs:
            try:
                input_def = InputDefinition(
                    name=inp.name,
                    display_name=getattr(inp, "display_name", inp.name),
                    type=self._map_agno_type(inp.type),
                    required=getattr(inp, "required", False),
                    description=getattr(inp, "description", ""),
                    default=getattr(inp, "default", None),
                    options=getattr(inp, "options", None),
                    min_value=getattr(inp, "min_value", None),
                    max_value=getattr(inp, "max_value", None),
                )
                converted.append(input_def)
            except Exception as e:
                logger.warning("Failed to convert input %s: %s", inp, str(e))

        return converted

    def _convert_agno_outputs(self, agno_outputs: list[Any] | None) -> list[OutputDefinition]:
        """Convert Agno output definitions to our format."""
        if not agno_outputs:
            return []

        converted = []
        for out in agno_outputs:
            try:
                output_def = OutputDefinition(
                    name=out.name,
                    display_name=getattr(out, "display_name", out.name),
                    type=self._map_agno_type(out.type),
                    description=getattr(out, "description", ""),
                )
                converted.append(output_def)
            except Exception as e:
                logger.warning("Failed to convert output %s: %s", out, str(e))

        return converted

    def _map_agno_type(self, agno_type: str) -> str:
        """Map Agno types to our standard types."""
        type_mapping = {
            "string": "str",
            "text": "str",
            "integer": "int",
            "number": "float",
            "float": "float",
            "boolean": "bool",
            "bool": "bool",
            "array": "list",
            "list": "list",
            "object": "dict",
            "dict": "dict",
            "document": "Data",
            "embedding": "Data",
            "vector": "Data",
            "file": "file",
            "image": "file",
            "audio": "file",
            "video": "file",
        }
        return type_mapping.get(agno_type.lower(), "str")

    async def validate_component_config(self, component_id: str, config: dict[str, Any]) -> dict[str, Any]:
        """Validate component configuration using Agno's validation."""
        try:
            # Get component metadata for validation schema
            metadata = await self.get_component_metadata(component_id)
            if not metadata:
                return {"valid": False, "errors": [f"Component {component_id} not found"]}

            # Use Agno's validation if available
            if hasattr(self.client, "validate_config"):
                validation_result = await self.client.validate_config(component_id, config)
                return {"valid": validation_result.is_valid, "errors": validation_result.errors or []}

            # Basic validation against schema
            errors = []
            schema = metadata.config_schema

            # Validate required fields
            for field, field_config in schema.items():
                if field_config.get("required", False) and field not in config:
                    errors.append(f"Required field '{field}' is missing")

            return {"valid": len(errors) == 0, "errors": errors}

        except Exception as e:
            logger.error("Config validation failed for %s: %s", component_id, str(e))
            return {"valid": False, "errors": [str(e)]}

    async def execute_component(self, context: ExecutionContext) -> ExecutionResult:
        """Execute a single Agno component."""
        if not self._initialized:
            raise FrameworkInitializationError("Agno adapter not initialized")

        start_time = time.time()
        component_id = context.component_id

        try:
            # Route to appropriate component type
            if component_id.startswith("agno-tool-"):
                result = await self._execute_tool(context)
            elif component_id.startswith("agno-model-"):
                result = await self._execute_model(context)
            elif component_id.startswith("agno-vectorstore-"):
                result = await self._execute_vector_store(context)
            elif component_id.startswith("agno-kb-"):
                result = await self._execute_knowledge_base(context)
            elif component_id.startswith("agno-embedding-"):
                result = await self._execute_embedding(context)
            elif component_id.startswith("agno-retriever-"):
                result = await self._execute_retriever(context)
            else:
                raise ComponentNotFoundError(f"Unknown Agno component type: {component_id}")

            execution_time = time.time() - start_time

            return self._create_execution_result(
                success=True,
                data=result,
                execution_time=execution_time,
                metadata={"component_id": component_id, "framework": "agno", "session_id": context.session_id},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Agno component execution failed: %s", str(e))

            return self._create_execution_result(
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={"component_id": component_id, "framework": "agno", "session_id": context.session_id},
            )

    async def _execute_tool(self, context: ExecutionContext) -> Any:
        """Execute an Agno tool."""
        tool_id = context.component_id.replace("agno-tool-", "")

        # Get tool instance
        tool = await self.client.tools.get(tool_id)

        # Execute tool with inputs and config
        result = await tool.execute(inputs=context.inputs, config=context.config, session_id=context.session_id)

        return result

    async def _execute_model(self, context: ExecutionContext) -> Any:
        """Execute an Agno model."""
        model_id = context.component_id.replace("agno-model-", "")

        # Get model instance
        model = await self.client.models.get(model_id)

        # Execute model generation
        result = await model.generate(inputs=context.inputs, config=context.config, session_id=context.session_id)

        return result

    async def _execute_vector_store(self, context: ExecutionContext) -> Any:
        """Execute an Agno vector store operation."""
        vs_id = context.component_id.replace("agno-vectorstore-", "")

        # Get vector store instance
        vector_store = await self.client.vector_stores.get(vs_id)

        # Determine operation based on inputs
        if "query" in context.inputs:
            # Search operation
            result = await vector_store.search(
                query=context.inputs["query"], k=context.inputs.get("k", 5), config=context.config
            )
        elif "documents" in context.inputs:
            # Add documents operation
            result = await vector_store.add_documents(documents=context.inputs["documents"], config=context.config)
        else:
            msg = "Vector store requires either 'query' for search or 'documents' for adding"
            raise ValueError(msg)

        return result

    async def _execute_knowledge_base(self, context: ExecutionContext) -> Any:
        """Execute an Agno knowledge base operation."""
        kb_id = context.component_id.replace("agno-kb-", "")

        # Get knowledge base instance
        kb = await self.client.knowledge_bases.get(kb_id)

        # Determine operation based on inputs
        if "query" in context.inputs:
            # Query operation
            result = await kb.query(query=context.inputs["query"], config=context.config)
        elif "documents" in context.inputs:
            # Add documents operation
            result = await kb.add_documents(documents=context.inputs["documents"], config=context.config)
        else:
            msg = "Knowledge base requires either 'query' or 'documents'"
            raise ValueError(msg)

        return result

    async def _execute_embedding(self, context: ExecutionContext) -> Any:
        """Execute an Agno embedding model."""
        embedding_id = context.component_id.replace("agno-embedding-", "")

        # Get embedding model instance
        embedding_model = await self.client.embeddings.get(embedding_id)

        # Generate embeddings
        result = await embedding_model.embed(texts=context.inputs.get("texts", []), config=context.config)

        return result

    async def _execute_retriever(self, context: ExecutionContext) -> Any:
        """Execute an Agno retriever."""
        retriever_id = context.component_id.replace("agno-retriever-", "")

        # Get retriever instance
        retriever = await self.client.retrievers.get(retriever_id)

        # Perform retrieval
        result = await retriever.retrieve(
            query=context.inputs["query"], k=context.inputs.get("k", 5), config=context.config
        )

        return result

    async def execute_flow(self, flow_data: dict[str, Any], context: dict[str, Any] | None = None) -> ExecutionResult:
        """Execute a complete Agno flow."""
        start_time = time.time()

        try:
            # Convert flow_data to Agno format
            agno_flow = self._convert_to_agno_flow(flow_data)

            # Execute flow using Agno's flow engine
            result = await self.client.flows.execute(flow=agno_flow, context=context or {})

            execution_time = time.time() - start_time

            return self._create_execution_result(
                success=True,
                data=result,
                execution_time=execution_time,
                metadata={"framework": "agno", "flow_id": flow_data.get("id"), "context": context},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error("Agno flow execution failed: %s", str(e))

            return self._create_execution_result(
                success=False,
                error=str(e),
                execution_time=execution_time,
                metadata={"framework": "agno", "flow_id": flow_data.get("id"), "context": context},
            )

    def _convert_to_agno_flow(self, flow_data: dict[str, Any]) -> dict[str, Any]:
        """Convert flow data to Agno flow format."""
        # Extract nodes and edges
        nodes = flow_data.get("nodes", [])
        edges = flow_data.get("edges", [])

        # Convert to Agno format
        agno_flow = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "name": flow_data.get("name", "Untitled Flow"),
                "description": flow_data.get("description", ""),
                "version": flow_data.get("version", "1.0.0"),
            },
        }

        # Convert nodes
        for node in nodes:
            agno_node = {
                "id": node["id"],
                "type": node.get("type", ""),
                "config": node.get("data", {}).get("node", {}).get("template", {}),
                "position": node.get("position", {"x": 0, "y": 0}),
            }
            agno_flow["nodes"].append(agno_node)

        # Convert edges
        for edge in edges:
            agno_edge = {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "source_handle": edge.get("sourceHandle"),
                "target_handle": edge.get("targetHandle"),
            }
            agno_flow["edges"].append(agno_edge)

        return agno_flow


# Simulated Agno Client for demonstration purposes
class SimulatedAgnoClient:
    """Simulated Agno client for testing and demonstration."""

    def __init__(self, **config):
        self.config = config
        self.tools = SimulatedService("tool")
        self.models = SimulatedService("model")
        self.vector_stores = SimulatedService("vectorstore")
        self.knowledge_bases = SimulatedService("knowledge_base")
        self.embeddings = SimulatedService("embedding")
        self.retrievers = SimulatedService("retriever")
        self.flows = SimulatedService("flow")

    async def initialize(self):
        """Initialize simulated client."""
        pass

    async def close(self):
        """Close simulated client."""
        pass

    async def ping(self):
        """Ping simulated service."""
        return {"response_time": 0.001}

    async def get_status(self):
        """Get simulated service status."""
        return {"status": "running", "components": 6}


class SimulatedService:
    """Simulated service for testing."""

    def __init__(self, service_type: str):
        self.service_type = service_type

    async def list(self):
        """List simulated items."""
        return [
            SimulatedItem(f"{self.service_type}_1", f"Sample {self.service_type.title()} 1"),
            SimulatedItem(f"{self.service_type}_2", f"Sample {self.service_type.title()} 2"),
        ]

    async def get(self, item_id: str):
        """Get simulated item."""
        return SimulatedItem(item_id, f"Sample {self.service_type.title()}")


class SimulatedItem:
    """Simulated item for testing."""

    def __init__(self, item_id: str, name: str):
        self.id = item_id
        self.name = name
        self.display_name = name
        self.description = f"Description for {name}"
        self.version = "1.0.0"
        self.inputs = []
        self.outputs = []
        self.config_schema = {}
        self.tags = []
        self.documentation_url = None

    async def execute(self, **kwargs):
        """Execute simulated item."""
        return f"Executed {self.name} with {kwargs}"

    async def generate(self, **kwargs):
        """Generate with simulated item."""
        return f"Generated with {self.name}: {kwargs}"

    async def search(self, **kwargs):
        """Search with simulated item."""
        return f"Search results from {self.name}: {kwargs}"

    async def add_documents(self, **kwargs):
        """Add documents to simulated item."""
        return f"Added documents to {self.name}: {kwargs}"

    async def query(self, **kwargs):
        """Query simulated item."""
        return f"Query results from {self.name}: {kwargs}"

    async def embed(self, **kwargs):
        """Embed with simulated item."""
        return f"Embeddings from {self.name}: {kwargs}"

    async def retrieve(self, **kwargs):
        """Retrieve with simulated item."""
        return f"Retrieved from {self.name}: {kwargs}"
