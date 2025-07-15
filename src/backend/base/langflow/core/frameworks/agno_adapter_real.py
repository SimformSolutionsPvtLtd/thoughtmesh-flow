"""Real Agno framework adapter implementation."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger

from langflow.core.frameworks.base import FrameworkAdapter
from langflow.core.frameworks.exceptions import ComponentDiscoveryError, ComponentExecutionError
from langflow.core.frameworks.types import (
    ComponentInfo,
    ComponentType,
    ExecutionResult,
    FrameworkConfig,
    FrameworkStatus,
)

try:
    # Try importing Agno dependencies
    from agno.agent import Agent
    from agno.knowledge.combined import CombinedKnowledgeBase
    from agno.knowledge.document import DocumentKnowledgeBase
    from agno.knowledge.pdf import PDFKnowledgeBase
    from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
    from agno.knowledge.website import WebsiteKnowledgeBase
    from agno.models.openai import OpenAIChat
    from agno.tools.calculator import CalculatorTools
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.tools.knowledge import KnowledgeTools
    from agno.tools.website import WebsiteTools
    from agno.tools.yfinance import YFinanceTools
    from agno.vectordb.lancedb import LanceDb
    from agno.vectordb.pgvector import PgVector

    AGNO_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Agno framework not available: {e}")
    AGNO_AVAILABLE = False
    # Define dummy classes to prevent import errors
    Agent = None
    CombinedKnowledgeBase = None
    DocumentKnowledgeBase = None
    PDFKnowledgeBase = None
    PDFUrlKnowledgeBase = None
    WebsiteKnowledgeBase = None
    OpenAIChat = None
    CalculatorTools = None
    DuckDuckGoTools = None
    KnowledgeTools = None
    WebsiteTools = None
    YFinanceTools = None
    LanceDb = None
    PgVector = None


class AgnoAdapterReal(FrameworkAdapter):
    """Real Agno framework adapter with actual component discovery and execution."""

    def __init__(self, config: Optional[FrameworkConfig] = None) -> None:
        """Initialize the Agno adapter."""
        super().__init__(config or FrameworkConfig())
        self._status = FrameworkStatus.UNKNOWN
        self._components_cache: Optional[List[ComponentInfo]] = None

    @property
    def name(self) -> str:
        """Get framework name."""
        return "agno"

    @property
    def version(self) -> str:
        """Get framework version."""
        try:
            import agno

            return getattr(agno, "__version__", "unknown")
        except ImportError:
            return "unavailable"

    async def initialize(self) -> bool:
        """Initialize the Agno framework."""
        try:
            if not AGNO_AVAILABLE:
                logger.warning("Agno framework is not available - skipping initialization")
                self._status = FrameworkStatus.ERROR
                return False

            # Test basic Agno functionality
            test_agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))
            if test_agent:
                logger.info("Agno framework initialized successfully")
                self._status = FrameworkStatus.READY
                return True
            else:
                self._status = FrameworkStatus.ERROR
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Agno framework: {e}")
            self._status = FrameworkStatus.ERROR
            return False

    async def get_status(self) -> FrameworkStatus:
        """Get current framework status."""
        if self._status == FrameworkStatus.UNKNOWN:
            await self.initialize()
        return self._status

    async def discover_components(self) -> List[ComponentInfo]:
        """Discover available Agno components."""
        if not AGNO_AVAILABLE:
            return []

        if self._components_cache is not None:
            return self._components_cache

        try:
            components = []

            # Models
            components.extend(
                [
                    ComponentInfo(
                        id="agno_openai_chat",
                        name="OpenAI Chat Model",
                        type=ComponentType.MODEL,
                        description="OpenAI language model for chat conversations",
                        framework="agno",
                        category="llm",
                        parameters={
                            "id": {
                                "type": "str",
                                "default": "gpt-4o-mini",
                                "options": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
                            },
                            "api_key": {"type": "str", "required": False, "description": "OpenAI API key"},
                            "temperature": {"type": "float", "default": 0.7, "min": 0.0, "max": 2.0},
                            "max_tokens": {
                                "type": "int",
                                "required": False,
                                "description": "Maximum tokens to generate",
                            },
                        },
                    ),
                ]
            )

            # Vector Stores
            components.extend(
                [
                    ComponentInfo(
                        id="agno_pgvector",
                        name="PgVector Database",
                        type=ComponentType.VECTOR_STORE,
                        description="PostgreSQL vector database for embeddings",
                        framework="agno",
                        category="vector_db",
                        parameters={
                            "table_name": {"type": "str", "required": True, "description": "Database table name"},
                            "db_url": {"type": "str", "required": True, "description": "PostgreSQL connection URL"},
                            "dimension": {"type": "int", "default": 1536, "description": "Vector dimension"},
                        },
                    ),
                    ComponentInfo(
                        id="agno_lancedb",
                        name="LanceDB",
                        type=ComponentType.VECTOR_STORE,
                        description="High-performance vector database",
                        framework="agno",
                        category="vector_db",
                        parameters={
                            "table_name": {"type": "str", "required": True, "description": "Table name"},
                            "uri": {"type": "str", "default": "tmp/lancedb", "description": "Database URI"},
                        },
                    ),
                ]
            )

            # Knowledge Bases
            components.extend(
                [
                    ComponentInfo(
                        id="agno_pdf_knowledge",
                        name="PDF Knowledge Base",
                        type=ComponentType.KNOWLEDGE_BASE,
                        description="Knowledge base for PDF documents",
                        framework="agno",
                        category="knowledge",
                        parameters={
                            "path": {"type": "str", "required": True, "description": "Path to PDF file or directory"},
                            "vector_db": {
                                "type": "object",
                                "required": True,
                                "description": "Vector database instance",
                            },
                        },
                    ),
                    ComponentInfo(
                        id="agno_pdf_url_knowledge",
                        name="PDF URL Knowledge Base",
                        type=ComponentType.KNOWLEDGE_BASE,
                        description="Knowledge base for PDF documents from URLs",
                        framework="agno",
                        category="knowledge",
                        parameters={
                            "urls": {"type": "list", "required": True, "description": "List of PDF URLs"},
                            "vector_db": {
                                "type": "object",
                                "required": True,
                                "description": "Vector database instance",
                            },
                        },
                    ),
                    ComponentInfo(
                        id="agno_website_knowledge",
                        name="Website Knowledge Base",
                        type=ComponentType.KNOWLEDGE_BASE,
                        description="Knowledge base for website content",
                        framework="agno",
                        category="knowledge",
                        parameters={
                            "urls": {"type": "list", "required": True, "description": "List of website URLs"},
                            "max_links": {"type": "int", "default": 10, "description": "Maximum links to crawl"},
                            "vector_db": {
                                "type": "object",
                                "required": True,
                                "description": "Vector database instance",
                            },
                        },
                    ),
                    ComponentInfo(
                        id="agno_document_knowledge",
                        name="Document Knowledge Base",
                        type=ComponentType.KNOWLEDGE_BASE,
                        description="Knowledge base for document collections",
                        framework="agno",
                        category="knowledge",
                        parameters={
                            "vector_db": {
                                "type": "object",
                                "required": True,
                                "description": "Vector database instance",
                            },
                        },
                    ),
                ]
            )

            # Tools
            components.extend(
                [
                    ComponentInfo(
                        id="agno_calculator_tools",
                        name="Calculator Tools",
                        type=ComponentType.TOOL,
                        description="Mathematical calculation tools",
                        framework="agno",
                        category="math",
                        parameters={
                            "enable_all": {
                                "type": "bool",
                                "default": True,
                                "description": "Enable all calculator functions",
                            },
                        },
                    ),
                    ComponentInfo(
                        id="agno_duckduckgo_tools",
                        name="DuckDuckGo Search Tools",
                        type=ComponentType.TOOL,
                        description="Web search using DuckDuckGo",
                        framework="agno",
                        category="search",
                        parameters={
                            "include_tools": {
                                "type": "list",
                                "required": False,
                                "description": "Specific tools to include",
                            },
                        },
                    ),
                    ComponentInfo(
                        id="agno_website_tools",
                        name="Website Tools",
                        type=ComponentType.TOOL,
                        description="Tools for interacting with websites",
                        framework="agno",
                        category="web",
                        parameters={
                            "knowledge_base": {
                                "type": "object",
                                "required": False,
                                "description": "Knowledge base for context",
                            },
                        },
                    ),
                    ComponentInfo(
                        id="agno_yfinance_tools",
                        name="Yahoo Finance Tools",
                        type=ComponentType.TOOL,
                        description="Financial data and stock market tools",
                        framework="agno",
                        category="finance",
                        parameters={},
                    ),
                    ComponentInfo(
                        id="agno_knowledge_tools",
                        name="Knowledge Tools",
                        type=ComponentType.TOOL,
                        description="Tools for knowledge base interaction",
                        framework="agno",
                        category="knowledge",
                        parameters={
                            "knowledge": {"type": "object", "required": True, "description": "Knowledge base instance"},
                            "think": {"type": "bool", "default": True, "description": "Enable thinking capability"},
                            "search": {"type": "bool", "default": True, "description": "Enable search capability"},
                            "analyze": {"type": "bool", "default": True, "description": "Enable analysis capability"},
                        },
                    ),
                ]
            )

            # Agents
            components.extend(
                [
                    ComponentInfo(
                        id="agno_agent",
                        name="Agno Agent",
                        type=ComponentType.AGENT,
                        description="General-purpose AI agent with tools and knowledge",
                        framework="agno",
                        category="agent",
                        parameters={
                            "model": {"type": "object", "required": True, "description": "Language model instance"},
                            "tools": {"type": "list", "required": False, "description": "List of tools"},
                            "knowledge": {"type": "object", "required": False, "description": "Knowledge base"},
                            "search_knowledge": {
                                "type": "bool",
                                "default": False,
                                "description": "Enable knowledge search",
                            },
                            "show_tool_calls": {
                                "type": "bool",
                                "default": False,
                                "description": "Show tool call details",
                            },
                            "markdown": {"type": "bool", "default": False, "description": "Use markdown formatting"},
                        },
                    ),
                ]
            )

            self._components_cache = components
            logger.info(f"Discovered {len(components)} Agno components")
            return components

        except Exception as e:
            error_msg = f"Failed to discover Agno components: {e}"
            logger.error(error_msg)
            raise ComponentDiscoveryError(error_msg) from e

    async def execute_component(
        self,
        component_id: str,
        parameters: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None,
    ) -> ExecutionResult:
        """Execute an Agno component."""
        if not AGNO_AVAILABLE:
            raise ComponentExecutionError("Agno framework is not available")

        try:
            logger.info(f"Executing Agno component: {component_id}")

            # Dispatch to specific component executors
            if component_id == "agno_openai_chat":
                return await self._execute_openai_chat(parameters)
            elif component_id == "agno_pgvector":
                return await self._execute_pgvector(parameters)
            elif component_id == "agno_lancedb":
                return await self._execute_lancedb(parameters)
            elif component_id == "agno_pdf_knowledge":
                return await self._execute_pdf_knowledge(parameters)
            elif component_id == "agno_pdf_url_knowledge":
                return await self._execute_pdf_url_knowledge(parameters)
            elif component_id == "agno_website_knowledge":
                return await self._execute_website_knowledge(parameters)
            elif component_id == "agno_document_knowledge":
                return await self._execute_document_knowledge(parameters)
            elif component_id == "agno_calculator_tools":
                return await self._execute_calculator_tools(parameters)
            elif component_id == "agno_duckduckgo_tools":
                return await self._execute_duckduckgo_tools(parameters)
            elif component_id == "agno_website_tools":
                return await self._execute_website_tools(parameters)
            elif component_id == "agno_yfinance_tools":
                return await self._execute_yfinance_tools(parameters)
            elif component_id == "agno_knowledge_tools":
                return await self._execute_knowledge_tools(parameters)
            elif component_id == "agno_agent":
                return await self._execute_agent(parameters, inputs)
            else:
                raise ComponentExecutionError(f"Unknown Agno component: {component_id}")

        except Exception as e:
            error_msg = f"Failed to execute Agno component {component_id}: {e}"
            logger.error(error_msg)
            raise ComponentExecutionError(error_msg) from e

    async def _execute_openai_chat(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute OpenAI chat model."""
        model = OpenAIChat(
            id=parameters.get("id", "gpt-4o-mini"),
            api_key=parameters.get("api_key"),
            temperature=parameters.get("temperature", 0.7),
            max_tokens=parameters.get("max_tokens"),
        )

        return ExecutionResult(
            success=True,
            output=model,
            metadata={
                "component_type": "model",
                "model_id": parameters.get("id", "gpt-4o-mini"),
            },
        )

    async def _execute_pgvector(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute PgVector database."""
        vector_db = PgVector(
            table_name=parameters["table_name"],
            db_url=parameters["db_url"],
            dimension=parameters.get("dimension", 1536),
        )

        return ExecutionResult(
            success=True,
            output=vector_db,
            metadata={
                "component_type": "vector_store",
                "table_name": parameters["table_name"],
            },
        )

    async def _execute_lancedb(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute LanceDB."""
        vector_db = LanceDb(
            table_name=parameters["table_name"],
            uri=parameters.get("uri", "tmp/lancedb"),
        )

        return ExecutionResult(
            success=True,
            output=vector_db,
            metadata={
                "component_type": "vector_store",
                "table_name": parameters["table_name"],
            },
        )

    async def _execute_pdf_knowledge(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute PDF knowledge base."""
        knowledge_base = PDFKnowledgeBase(
            path=parameters["path"],
            vector_db=parameters["vector_db"],
        )

        return ExecutionResult(
            success=True,
            output=knowledge_base,
            metadata={
                "component_type": "knowledge_base",
                "source_type": "pdf",
            },
        )

    async def _execute_pdf_url_knowledge(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute PDF URL knowledge base."""
        knowledge_base = PDFUrlKnowledgeBase(
            urls=parameters["urls"],
            vector_db=parameters["vector_db"],
        )

        return ExecutionResult(
            success=True,
            output=knowledge_base,
            metadata={
                "component_type": "knowledge_base",
                "source_type": "pdf_url",
                "url_count": len(parameters["urls"]),
            },
        )

    async def _execute_website_knowledge(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute website knowledge base."""
        knowledge_base = WebsiteKnowledgeBase(
            urls=parameters["urls"],
            max_links=parameters.get("max_links", 10),
            vector_db=parameters["vector_db"],
        )

        return ExecutionResult(
            success=True,
            output=knowledge_base,
            metadata={
                "component_type": "knowledge_base",
                "source_type": "website",
                "url_count": len(parameters["urls"]),
            },
        )

    async def _execute_document_knowledge(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute document knowledge base."""
        knowledge_base = DocumentKnowledgeBase(
            vector_db=parameters["vector_db"],
        )

        return ExecutionResult(
            success=True,
            output=knowledge_base,
            metadata={
                "component_type": "knowledge_base",
                "source_type": "document",
            },
        )

    async def _execute_calculator_tools(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute calculator tools."""
        tools = CalculatorTools(
            enable_all=parameters.get("enable_all", True),
        )

        return ExecutionResult(
            success=True,
            output=tools,
            metadata={
                "component_type": "tool",
                "tool_category": "math",
            },
        )

    async def _execute_duckduckgo_tools(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute DuckDuckGo search tools."""
        tools = DuckDuckGoTools(
            include_tools=parameters.get("include_tools"),
        )

        return ExecutionResult(
            success=True,
            output=tools,
            metadata={
                "component_type": "tool",
                "tool_category": "search",
            },
        )

    async def _execute_website_tools(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute website tools."""
        tools = WebsiteTools(
            knowledge_base=parameters.get("knowledge_base"),
        )

        return ExecutionResult(
            success=True,
            output=tools,
            metadata={
                "component_type": "tool",
                "tool_category": "web",
            },
        )

    async def _execute_yfinance_tools(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute Yahoo Finance tools."""
        tools = YFinanceTools()

        return ExecutionResult(
            success=True,
            output=tools,
            metadata={
                "component_type": "tool",
                "tool_category": "finance",
            },
        )

    async def _execute_knowledge_tools(self, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute knowledge tools."""
        tools = KnowledgeTools(
            knowledge=parameters["knowledge"],
            think=parameters.get("think", True),
            search=parameters.get("search", True),
            analyze=parameters.get("analyze", True),
        )

        return ExecutionResult(
            success=True,
            output=tools,
            metadata={
                "component_type": "tool",
                "tool_category": "knowledge",
            },
        )

    async def _execute_agent(self, parameters: Dict[str, Any], inputs: Optional[Dict[str, Any]]) -> ExecutionResult:
        """Execute Agno agent."""
        agent = Agent(
            model=parameters["model"],
            tools=parameters.get("tools", []),
            knowledge=parameters.get("knowledge"),
            search_knowledge=parameters.get("search_knowledge", False),
            show_tool_calls=parameters.get("show_tool_calls", False),
            markdown=parameters.get("markdown", False),
        )

        # If there are inputs, try to execute the agent
        result = None
        if inputs and "message" in inputs:
            try:
                # Use the synchronous response method for now
                result = agent.print_response(
                    inputs["message"],
                    markdown=parameters.get("markdown", False),
                )
            except Exception as e:
                logger.warning(f"Agent execution failed, returning agent instance: {e}")

        return ExecutionResult(
            success=True,
            output=result if result is not None else agent,
            metadata={
                "component_type": "agent",
                "has_tools": len(parameters.get("tools", [])) > 0,
                "has_knowledge": parameters.get("knowledge") is not None,
            },
        )

    async def cleanup(self) -> None:
        """Clean up Agno adapter resources."""
        try:
            # Clear component cache
            self._components_cache = None
            self._status = FrameworkStatus.UNKNOWN
            logger.info("Agno adapter cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during Agno adapter cleanup: {e}")
