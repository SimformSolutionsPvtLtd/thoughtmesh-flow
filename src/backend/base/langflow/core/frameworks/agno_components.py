"""
Real Agno Components Implementation
This module implements actual Agno framework components based on the agno-agi/agno repository structure.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .types import ComponentCategory, ComponentMetadata, InputDefinition, OutputDefinition, FrameworkType


class AgnoComponentRegistry:
    """Registry for all Agno framework components."""

    @staticmethod
    def get_all_components() -> List[ComponentMetadata]:
        """Get all available Agno components."""
        components = []

        # Add all component types
        components.extend(AgnoComponentRegistry._get_model_components())
        components.extend(AgnoComponentRegistry._get_tool_components())
        components.extend(AgnoComponentRegistry._get_vector_store_components())
        components.extend(AgnoComponentRegistry._get_knowledge_base_components())
        components.extend(AgnoComponentRegistry._get_embedding_components())
        components.extend(AgnoComponentRegistry._get_memory_components())
        components.extend(AgnoComponentRegistry._get_storage_components())
        components.extend(AgnoComponentRegistry._get_reranker_components())
        components.extend(AgnoComponentRegistry._get_chunking_components())
        components.extend(AgnoComponentRegistry._get_document_reader_components())
        components.extend(AgnoComponentRegistry._get_agent_components())
        components.extend(AgnoComponentRegistry._get_team_components())
        components.extend(AgnoComponentRegistry._get_workflow_components())

        return components

    @staticmethod
    def _get_model_components() -> List[ComponentMetadata]:
        """Get model components."""
        return [
            ComponentMetadata(
                id="agno_openai_chat",
                name="OpenAI Chat",
                display_name="OpenAI Chat Model",
                description="OpenAI GPT models for chat completion",
                category=ComponentCategory.MODELS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=True,
                        description="OpenAI model identifier",
                        default="gpt-4o",
                        options=["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "o1-mini", "o1-preview"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="OpenAI API key (uses environment variable if not provided)",
                    ),
                    InputDefinition(
                        name="temperature",
                        display_name="Temperature",
                        type="number",
                        required=False,
                        description="Sampling temperature",
                        default=0.7,
                        min_value=0.0,
                        max_value=2.0,
                    ),
                    InputDefinition(
                        name="max_tokens",
                        display_name="Max Tokens",
                        type="number",
                        required=False,
                        description="Maximum tokens to generate",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="model",
                        display_name="Model Instance",
                        type="Model",
                        description="Configured OpenAI chat model",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_anthropic_claude",
                name="Anthropic Claude",
                display_name="Anthropic Claude Model",
                description="Anthropic's Claude models for advanced reasoning",
                category=ComponentCategory.MODELS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=True,
                        description="Claude model identifier",
                        default="claude-3-5-sonnet-20241022",
                        options=["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="Anthropic API key",
                    ),
                    InputDefinition(
                        name="temperature",
                        display_name="Temperature",
                        type="number",
                        required=False,
                        description="Sampling temperature",
                        default=0.7,
                        min_value=0.0,
                        max_value=1.0,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="model", display_name="Model Instance", type="Model", description="Configured Claude model"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_groq_llama",
                name="Groq Llama",
                display_name="Groq Llama Model",
                description="Groq's lightning-fast Llama models",
                category=ComponentCategory.MODELS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=True,
                        description="Groq model identifier",
                        default="llama-3.3-70b-versatile",
                        options=["llama-3.3-70b-versatile", "llama-3.2-90b-text-preview", "llama-3.1-8b-instant"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="Groq API key",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="model", display_name="Model Instance", type="Model", description="Configured Groq model"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_ollama",
                name="Ollama",
                display_name="Ollama Local Model",
                description="Local Ollama models for privacy-focused AI",
                category=ComponentCategory.MODELS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=True,
                        description="Ollama model identifier",
                        default="llama3.1:8b",
                        options=["llama3.1:8b", "llama3.2:3b", "mistral:7b", "phi3:3.8b"],
                    ),
                    InputDefinition(
                        name="base_url",
                        display_name="Base URL",
                        type="string",
                        required=False,
                        description="Ollama server URL",
                        default="http://localhost:11434",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="model", display_name="Model Instance", type="Model", description="Configured Ollama model"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_google_gemini",
                name="Google Gemini",
                display_name="Google Gemini Model",
                description="Google's Gemini models with multimodal capabilities",
                category=ComponentCategory.MODELS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=True,
                        description="Gemini model identifier",
                        default="gemini-2.0-flash-exp",
                        options=["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="Google AI API key",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="model", display_name="Model Instance", type="Model", description="Configured Gemini model"
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_tool_components() -> List[ComponentMetadata]:
        """Get tool components."""
        return [
            ComponentMetadata(
                id="agno_duckduckgo_tools",
                name="DuckDuckGo Search",
                display_name="DuckDuckGo Search Tools",
                description="Web search tools powered by DuckDuckGo",
                category=ComponentCategory.TOOLS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="num_results",
                        display_name="Number of Results",
                        type="number",
                        required=False,
                        description="Number of search results to return",
                        default=5,
                        min_value=1,
                        max_value=20,
                    ),
                    InputDefinition(
                        name="cache_results",
                        display_name="Cache Results",
                        type="boolean",
                        required=False,
                        description="Cache search results for faster repeated queries",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="tools",
                        display_name="Tool Instance",
                        type="Toolkit",
                        description="DuckDuckGo search toolkit",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_yfinance_tools",
                name="Yahoo Finance",
                display_name="Yahoo Finance Tools",
                description="Financial data and stock information tools",
                category=ComponentCategory.TOOLS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="stock_price",
                        display_name="Enable Stock Price",
                        type="boolean",
                        required=False,
                        description="Enable stock price retrieval",
                        default=True,
                    ),
                    InputDefinition(
                        name="company_info",
                        display_name="Enable Company Info",
                        type="boolean",
                        required=False,
                        description="Enable company information retrieval",
                        default=True,
                    ),
                    InputDefinition(
                        name="analyst_recommendations",
                        display_name="Enable Analyst Recommendations",
                        type="boolean",
                        required=False,
                        description="Enable analyst recommendations",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="tools", display_name="Tool Instance", type="Toolkit", description="Yahoo Finance toolkit"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_arxiv_tools",
                name="ArXiv Research",
                display_name="ArXiv Research Tools",
                description="Academic paper search and download from ArXiv",
                category=ComponentCategory.TOOLS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="download_dir",
                        display_name="Download Directory",
                        type="string",
                        required=False,
                        description="Directory to download papers",
                        default="./arxiv_papers",
                    ),
                    InputDefinition(
                        name="max_results",
                        display_name="Max Results",
                        type="number",
                        required=False,
                        description="Maximum number of papers to return",
                        default=10,
                        min_value=1,
                        max_value=100,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="tools", display_name="Tool Instance", type="Toolkit", description="ArXiv research toolkit"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_file_tools",
                name="File Operations",
                display_name="File Management Tools",
                description="Tools for reading, writing, and managing files",
                category=ComponentCategory.TOOLS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="base_dir",
                        display_name="Base Directory",
                        type="string",
                        required=False,
                        description="Base directory for file operations",
                        default="./workspace",
                    ),
                    InputDefinition(
                        name="read_files",
                        display_name="Enable Read Files",
                        type="boolean",
                        required=False,
                        description="Allow reading files",
                        default=True,
                    ),
                    InputDefinition(
                        name="save_files",
                        display_name="Enable Save Files",
                        type="boolean",
                        required=False,
                        description="Allow saving files",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="tools",
                        display_name="Tool Instance",
                        type="Toolkit",
                        description="File management toolkit",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_calculator_tools",
                name="Calculator",
                display_name="Calculator Tools",
                description="Mathematical calculation tools",
                category=ComponentCategory.TOOLS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="enable_all",
                        display_name="Enable All Functions",
                        type="boolean",
                        required=False,
                        description="Enable all calculator functions",
                        default=True,
                    )
                ],
                outputs=[
                    OutputDefinition(
                        name="tools", display_name="Tool Instance", type="Toolkit", description="Calculator toolkit"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_reasoning_tools",
                name="Reasoning Tools",
                display_name="Reasoning and Logic Tools",
                description="Advanced reasoning and chain-of-thought tools",
                category=ComponentCategory.TOOLS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="add_instructions",
                        display_name="Add Instructions",
                        type="boolean",
                        required=False,
                        description="Add reasoning instructions to agent",
                        default=True,
                    ),
                    InputDefinition(
                        name="add_few_shot",
                        display_name="Add Few-Shot Examples",
                        type="boolean",
                        required=False,
                        description="Add few-shot reasoning examples",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="tools", display_name="Tool Instance", type="Toolkit", description="Reasoning toolkit"
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_vector_store_components() -> List[ComponentMetadata]:
        """Get vector store components."""
        return [
            ComponentMetadata(
                id="agno_pgvector",
                name="PgVector",
                display_name="PostgreSQL with pgvector",
                description="PostgreSQL database with vector similarity search",
                category=ComponentCategory.VECTOR_STORES,
                framework=FrameworkType.AGNO,
                icon="cpu",
                inputs=[
                    InputDefinition(
                        name="db_url",
                        display_name="Database URL",
                        type="string",
                        required=True,
                        description="PostgreSQL connection string",
                        default="postgresql+psycopg://ai:ai@localhost:5532/ai",
                    ),
                    InputDefinition(
                        name="table_name",
                        display_name="Table Name",
                        type="string",
                        required=True,
                        description="Table name for storing vectors",
                        default="vector_store",
                    ),
                    InputDefinition(
                        name="distance",
                        display_name="Distance Metric",
                        type="string",
                        required=False,
                        description="Distance metric for similarity search",
                        default="cosine",
                        options=["cosine", "l2", "max_inner_product"],
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        description="Configured PgVector database",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_lancedb",
                name="LanceDB",
                display_name="LanceDB Vector Store",
                description="Fast vector database with hybrid search capabilities",
                category=ComponentCategory.VECTOR_STORES,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="uri",
                        display_name="Database URI",
                        type="string",
                        required=False,
                        description="LanceDB URI or path",
                        default="/tmp/lancedb",
                    ),
                    InputDefinition(
                        name="table_name",
                        display_name="Table Name",
                        type="string",
                        required=True,
                        description="Table name for storing vectors",
                        default="vectors",
                    ),
                    InputDefinition(
                        name="search_type",
                        display_name="Search Type",
                        type="string",
                        required=False,
                        description="Type of search to perform",
                        default="vector",
                        options=["vector", "keyword", "hybrid"],
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        description="Configured LanceDB database",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_qdrant",
                name="Qdrant",
                display_name="Qdrant Vector Database",
                description="High-performance vector similarity search engine",
                category=ComponentCategory.VECTOR_STORES,
                framework=FrameworkType.AGNO,
                icon="Qdrant",
                inputs=[
                    InputDefinition(
                        name="url",
                        display_name="Qdrant URL",
                        type="string",
                        required=False,
                        description="Qdrant server URL",
                        default="http://localhost:6333",
                    ),
                    InputDefinition(
                        name="collection",
                        display_name="Collection Name",
                        type="string",
                        required=True,
                        description="Collection name for storing vectors",
                        default="documents",
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="Qdrant API key for authentication",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        description="Configured Qdrant database",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_milvus",
                name="Milvus",
                display_name="Milvus Vector Database",
                description="Scalable vector database for large-scale similarity search",
                category=ComponentCategory.VECTOR_STORES,
                framework=FrameworkType.AGNO,
                icon="Milvus",
                inputs=[
                    InputDefinition(
                        name="uri",
                        display_name="Milvus URI",
                        type="string",
                        required=False,
                        description="Milvus connection URI",
                        default="tmp/milvus.db",
                    ),
                    InputDefinition(
                        name="collection",
                        display_name="Collection Name",
                        type="string",
                        required=True,
                        description="Collection name for storing vectors",
                        default="documents",
                    ),
                    InputDefinition(
                        name="search_type",
                        display_name="Search Type",
                        type="string",
                        required=False,
                        description="Search type for retrieval",
                        default="vector",
                        options=["vector", "hybrid"],
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        description="Configured Milvus database",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_pinecone",
                name="Pinecone",
                display_name="Pinecone Vector Database",
                description="Managed vector database service with high performance",
                category=ComponentCategory.VECTOR_STORES,
                framework=FrameworkType.AGNO,
                icon="Pinecone",
                inputs=[
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=True,
                        description="Pinecone API key",
                    ),
                    InputDefinition(
                        name="index_name",
                        display_name="Index Name",
                        type="string",
                        required=True,
                        description="Pinecone index name",
                        default="documents",
                    ),
                    InputDefinition(
                        name="environment",
                        display_name="Environment",
                        type="string",
                        required=True,
                        description="Pinecone environment",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        description="Configured Pinecone database",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_knowledge_base_components() -> List[ComponentMetadata]:
        """Get knowledge base components."""
        return [
            ComponentMetadata(
                id="agno_pdf_url_knowledge",
                name="PDF URL Knowledge Base",
                display_name="PDF from URL Knowledge Base",
                description="Knowledge base that loads PDFs from URLs",
                category=ComponentCategory.KNOWLEDGE_BASES,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="urls",
                        display_name="PDF URLs",
                        type="list",
                        required=True,
                        description="List of PDF URLs to load",
                    ),
                    InputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        required=True,
                        description="Vector database for storing embeddings",
                    ),
                    InputDefinition(
                        name="num_documents",
                        display_name="Number of Documents",
                        type="number",
                        required=False,
                        description="Number of relevant documents to retrieve",
                        default=5,
                        min_value=1,
                        max_value=50,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="knowledge_base",
                        display_name="Knowledge Base",
                        type="AgentKnowledge",
                        description="Configured PDF knowledge base",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_website_knowledge",
                name="Website Knowledge Base",
                display_name="Website Content Knowledge Base",
                description="Knowledge base that crawls and indexes website content",
                category=ComponentCategory.KNOWLEDGE_BASES,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="urls",
                        display_name="Website URLs",
                        type="list",
                        required=True,
                        description="List of website URLs to crawl",
                    ),
                    InputDefinition(
                        name="max_links",
                        display_name="Max Links",
                        type="number",
                        required=False,
                        description="Maximum number of links to crawl",
                        default=10,
                        min_value=1,
                        max_value=100,
                    ),
                    InputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        required=True,
                        description="Vector database for storing embeddings",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="knowledge_base",
                        display_name="Knowledge Base",
                        type="AgentKnowledge",
                        description="Configured website knowledge base",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_document_knowledge",
                name="Document Knowledge Base",
                display_name="Document Collection Knowledge Base",
                description="Knowledge base for document collections with metadata",
                category=ComponentCategory.KNOWLEDGE_BASES,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="documents",
                        display_name="Documents",
                        type="list",
                        required=True,
                        description="List of documents with metadata",
                    ),
                    InputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        required=True,
                        description="Vector database for storing embeddings",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="knowledge_base",
                        display_name="Knowledge Base",
                        type="AgentKnowledge",
                        description="Configured document knowledge base",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_combined_knowledge",
                name="Combined Knowledge Base",
                display_name="Combined Knowledge Sources",
                description="Combines multiple knowledge sources into one",
                category=ComponentCategory.KNOWLEDGE_BASES,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="sources",
                        display_name="Knowledge Sources",
                        type="list",
                        required=True,
                        description="List of knowledge base sources to combine",
                    ),
                    InputDefinition(
                        name="vector_db",
                        display_name="Vector Database",
                        type="VectorDb",
                        required=True,
                        description="Vector database for combined storage",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="knowledge_base",
                        display_name="Knowledge Base",
                        type="AgentKnowledge",
                        description="Combined knowledge base",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_embedding_components() -> List[ComponentMetadata]:
        """Get embedding components."""
        return [
            ComponentMetadata(
                id="agno_openai_embedder",
                name="OpenAI Embeddings",
                display_name="OpenAI Text Embeddings",
                description="OpenAI's text embedding models",
                category=ComponentCategory.EMBEDDINGS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=False,
                        description="OpenAI embedding model",
                        default="text-embedding-3-small",
                        options=["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="OpenAI API key",
                    ),
                    InputDefinition(
                        name="dimensions",
                        display_name="Dimensions",
                        type="number",
                        required=False,
                        description="Embedding dimensions",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="embedder",
                        display_name="Embedder",
                        type="Embedder",
                        description="Configured OpenAI embedder",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_cohere_embedder",
                name="Cohere Embeddings",
                display_name="Cohere Text Embeddings",
                description="Cohere's multilingual embedding models",
                category=ComponentCategory.EMBEDDINGS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=False,
                        description="Cohere embedding model",
                        default="embed-v4.0",
                        options=["embed-v4.0", "embed-multilingual-v3.0"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="Cohere API key",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="embedder",
                        display_name="Embedder",
                        type="Embedder",
                        description="Configured Cohere embedder",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_huggingface_embedder",
                name="HuggingFace Embeddings",
                display_name="HuggingFace Text Embeddings",
                description="HuggingFace transformer-based embeddings",
                category=ComponentCategory.EMBEDDINGS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_name",
                        display_name="Model Name",
                        type="string",
                        required=False,
                        description="HuggingFace model name",
                        default="sentence-transformers/all-MiniLM-L6-v2",
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="HuggingFace API key",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="embedder",
                        display_name="Embedder",
                        type="Embedder",
                        description="Configured HuggingFace embedder",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_ollama_embedder",
                name="Ollama Embeddings",
                display_name="Ollama Local Embeddings",
                description="Local embedding models via Ollama",
                category=ComponentCategory.EMBEDDINGS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model_id",
                        display_name="Model ID",
                        type="string",
                        required=False,
                        description="Ollama embedding model",
                        default="nomic-embed-text",
                        options=["nomic-embed-text", "mxbai-embed-large"],
                    ),
                    InputDefinition(
                        name="base_url",
                        display_name="Base URL",
                        type="string",
                        required=False,
                        description="Ollama server URL",
                        default="http://localhost:11434",
                    ),
                    InputDefinition(
                        name="dimensions",
                        display_name="Dimensions",
                        type="number",
                        required=False,
                        description="Embedding dimensions",
                        default=768,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="embedder",
                        display_name="Embedder",
                        type="Embedder",
                        description="Configured Ollama embedder",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_memory_components() -> List[ComponentMetadata]:
        """Get memory components."""
        return [
            ComponentMetadata(
                id="agno_agent_memory",
                name="Agent Memory",
                display_name="Agent Conversation Memory",
                description="Memory system for storing agent conversations",
                category=ComponentCategory.MEMORY,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="db_url",
                        display_name="Database URL",
                        type="string",
                        required=True,
                        description="Database connection for memory storage",
                    ),
                    InputDefinition(
                        name="table_name",
                        display_name="Table Name",
                        type="string",
                        required=False,
                        description="Table name for memory storage",
                        default="agent_memory",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="memory",
                        display_name="Memory Instance",
                        type="Memory",
                        description="Configured agent memory",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_user_memory",
                name="User Memory",
                display_name="User-Specific Memory",
                description="Memory system for storing user-specific information",
                category=ComponentCategory.MEMORY,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="db_url",
                        display_name="Database URL",
                        type="string",
                        required=True,
                        description="Database connection for user memory",
                    ),
                    InputDefinition(
                        name="user_id",
                        display_name="User ID",
                        type="string",
                        required=True,
                        description="Unique identifier for the user",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="memory",
                        display_name="Memory Instance",
                        type="Memory",
                        description="Configured user memory",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_team_memory",
                name="Team Memory",
                display_name="Team Shared Memory",
                description="Shared memory system for agent teams",
                category=ComponentCategory.MEMORY,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="db_url",
                        display_name="Database URL",
                        type="string",
                        required=True,
                        description="Database connection for team memory",
                    ),
                    InputDefinition(
                        name="team_id",
                        display_name="Team ID",
                        type="string",
                        required=True,
                        description="Unique identifier for the team",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="memory",
                        display_name="Memory Instance",
                        type="Memory",
                        description="Configured team memory",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_storage_components() -> List[ComponentMetadata]:
        """Get storage components."""
        return [
            ComponentMetadata(
                id="agno_sqlite_storage",
                name="SQLite Storage",
                display_name="SQLite Agent Storage",
                description="SQLite-based storage for agent sessions",
                category=ComponentCategory.STORAGE,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="db_file",
                        display_name="Database File",
                        type="string",
                        required=False,
                        description="SQLite database file path",
                        default="agent_storage.db",
                    ),
                    InputDefinition(
                        name="table_name",
                        display_name="Table Name",
                        type="string",
                        required=False,
                        description="Table name for session storage",
                        default="agent_sessions",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="storage",
                        display_name="Storage Instance",
                        type="Storage",
                        description="Configured SQLite storage",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_postgres_storage",
                name="PostgreSQL Storage",
                display_name="PostgreSQL Agent Storage",
                description="PostgreSQL-based storage for agent sessions",
                category=ComponentCategory.STORAGE,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="db_url",
                        display_name="Database URL",
                        type="string",
                        required=True,
                        description="PostgreSQL connection string",
                    ),
                    InputDefinition(
                        name="table_name",
                        display_name="Table Name",
                        type="string",
                        required=False,
                        description="Table name for session storage",
                        default="agent_sessions",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="storage",
                        display_name="Storage Instance",
                        type="Storage",
                        description="Configured PostgreSQL storage",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_reranker_components() -> List[ComponentMetadata]:
        """Get reranker components."""
        return [
            ComponentMetadata(
                id="agno_cohere_reranker",
                name="Cohere Reranker",
                display_name="Cohere Reranking Model",
                description="Cohere's reranking models for improving search results",
                category=ComponentCategory.RERANKERS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model",
                        display_name="Model",
                        type="string",
                        required=False,
                        description="Cohere reranking model",
                        default="rerank-multilingual-v3.0",
                        options=["rerank-multilingual-v3.0", "rerank-english-v3.0"],
                    ),
                    InputDefinition(
                        name="api_key",
                        display_name="API Key",
                        type="string",
                        required=False,
                        description="Cohere API key",
                    ),
                    InputDefinition(
                        name="top_n",
                        display_name="Top N",
                        type="number",
                        required=False,
                        description="Number of top results to return",
                        default=5,
                        min_value=1,
                        max_value=50,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="reranker",
                        display_name="Reranker",
                        type="Reranker",
                        description="Configured Cohere reranker",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_sentence_transformer_reranker",
                name="Sentence Transformer Reranker",
                display_name="Sentence Transformer Reranking",
                description="Local reranking using sentence transformers",
                category=ComponentCategory.RERANKERS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model",
                        display_name="Model",
                        type="string",
                        required=False,
                        description="Sentence transformer reranking model",
                        default="BAAI/bge-reranker-v2-m3",
                        options=["BAAI/bge-reranker-v2-m3", "BAAI/bge-reranker-base"],
                    ),
                    InputDefinition(
                        name="top_n",
                        display_name="Top N",
                        type="number",
                        required=False,
                        description="Number of top results to return",
                        default=5,
                        min_value=1,
                        max_value=50,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="reranker",
                        display_name="Reranker",
                        type="Reranker",
                        description="Configured sentence transformer reranker",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_chunking_components() -> List[ComponentMetadata]:
        """Get chunking strategy components."""
        return [
            ComponentMetadata(
                id="agno_fixed_size_chunking",
                name="Fixed Size Chunking",
                display_name="Fixed Size Text Chunking",
                description="Split text into fixed-size chunks with overlap",
                category=ComponentCategory.CHUNKING,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="chunk_size",
                        display_name="Chunk Size",
                        type="number",
                        required=False,
                        description="Size of each text chunk",
                        default=1000,
                        min_value=100,
                        max_value=10000,
                    ),
                    InputDefinition(
                        name="overlap",
                        display_name="Overlap",
                        type="number",
                        required=False,
                        description="Overlap between chunks",
                        default=200,
                        min_value=0,
                        max_value=1000,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="chunking_strategy",
                        display_name="Chunking Strategy",
                        type="ChunkingStrategy",
                        description="Fixed size chunking strategy",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_recursive_chunking",
                name="Recursive Chunking",
                display_name="Recursive Text Chunking",
                description="Recursively split text using multiple separators",
                category=ComponentCategory.CHUNKING,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="chunk_size",
                        display_name="Chunk Size",
                        type="number",
                        required=False,
                        description="Target size of each chunk",
                        default=1000,
                        min_value=100,
                        max_value=10000,
                    ),
                    InputDefinition(
                        name="overlap",
                        display_name="Overlap",
                        type="number",
                        required=False,
                        description="Overlap between chunks",
                        default=200,
                        min_value=0,
                        max_value=1000,
                    ),
                    InputDefinition(
                        name="separators",
                        display_name="Separators",
                        type="list",
                        required=False,
                        description="List of separators to use for splitting",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="chunking_strategy",
                        display_name="Chunking Strategy",
                        type="ChunkingStrategy",
                        description="Recursive chunking strategy",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_semantic_chunking",
                name="Semantic Chunking",
                display_name="Semantic Text Chunking",
                description="Split text based on semantic similarity",
                category=ComponentCategory.CHUNKING,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="similarity_threshold",
                        display_name="Similarity Threshold",
                        type="number",
                        required=False,
                        description="Threshold for semantic similarity",
                        default=0.5,
                        min_value=0.0,
                        max_value=1.0,
                    ),
                    InputDefinition(
                        name="max_chunk_size",
                        display_name="Max Chunk Size",
                        type="number",
                        required=False,
                        description="Maximum size of chunks",
                        default=1000,
                        min_value=100,
                        max_value=10000,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="chunking_strategy",
                        display_name="Chunking Strategy",
                        type="ChunkingStrategy",
                        description="Semantic chunking strategy",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_agentic_chunking",
                name="Agentic Chunking",
                display_name="AI-Powered Agentic Chunking",
                description="Use AI to intelligently chunk documents",
                category=ComponentCategory.CHUNKING,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model",
                        display_name="AI Model",
                        type="Model",
                        required=False,
                        description="AI model for intelligent chunking",
                    ),
                    InputDefinition(
                        name="max_chunk_size",
                        display_name="Max Chunk Size",
                        type="number",
                        required=False,
                        description="Maximum size of chunks",
                        default=1000,
                        min_value=100,
                        max_value=10000,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="chunking_strategy",
                        display_name="Chunking Strategy",
                        type="ChunkingStrategy",
                        description="Agentic chunking strategy",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_document_reader_components() -> List[ComponentMetadata]:
        """Get document reader components."""
        return [
            ComponentMetadata(
                id="agno_pdf_reader",
                name="PDF Reader",
                display_name="PDF Document Reader",
                description="Read and extract text from PDF documents",
                category=ComponentCategory.DOCUMENT_READERS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="extract_images",
                        display_name="Extract Images",
                        type="boolean",
                        required=False,
                        description="Extract images from PDF",
                        default=False,
                    ),
                    InputDefinition(
                        name="extract_tables",
                        display_name="Extract Tables",
                        type="boolean",
                        required=False,
                        description="Extract tables from PDF",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="reader",
                        display_name="Document Reader",
                        type="Reader",
                        description="Configured PDF reader",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_docx_reader",
                name="DOCX Reader",
                display_name="Word Document Reader",
                description="Read and extract text from Word documents",
                category=ComponentCategory.DOCUMENT_READERS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="extract_tables",
                        display_name="Extract Tables",
                        type="boolean",
                        required=False,
                        description="Extract tables from DOCX",
                        default=True,
                    ),
                    InputDefinition(
                        name="preserve_formatting",
                        display_name="Preserve Formatting",
                        type="boolean",
                        required=False,
                        description="Preserve text formatting",
                        default=False,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="reader",
                        display_name="Document Reader",
                        type="Reader",
                        description="Configured DOCX reader",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_url_reader",
                name="URL Reader",
                display_name="Web Content Reader",
                description="Read and extract content from web pages",
                category=ComponentCategory.DOCUMENT_READERS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="timeout",
                        display_name="Timeout",
                        type="number",
                        required=False,
                        description="Request timeout in seconds",
                        default=30,
                        min_value=5,
                        max_value=300,
                    ),
                    InputDefinition(
                        name="follow_redirects",
                        display_name="Follow Redirects",
                        type="boolean",
                        required=False,
                        description="Follow HTTP redirects",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="reader",
                        display_name="Document Reader",
                        type="Reader",
                        description="Configured URL reader",
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_agent_components() -> List[ComponentMetadata]:
        """Get agent components."""
        return [
            ComponentMetadata(
                id="agno_basic_agent",
                name="Basic Agent",
                display_name="Basic AI Agent",
                description="A basic AI agent with model and tools",
                category=ComponentCategory.AGENTS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model",
                        display_name="AI Model",
                        type="Model",
                        required=True,
                        description="AI model for the agent",
                    ),
                    InputDefinition(
                        name="tools",
                        display_name="Tools",
                        type="list",
                        required=False,
                        description="List of tools for the agent",
                    ),
                    InputDefinition(
                        name="instructions",
                        display_name="Instructions",
                        type="string",
                        required=False,
                        description="Instructions for the agent behavior",
                    ),
                    InputDefinition(
                        name="description",
                        display_name="Description",
                        type="string",
                        required=False,
                        description="Description of the agent's role",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="agent", display_name="Agent", type="Agent", description="Configured AI agent"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_knowledge_agent",
                name="Knowledge Agent",
                display_name="Knowledge-Enhanced Agent",
                description="AI agent with knowledge base integration",
                category=ComponentCategory.AGENTS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model",
                        display_name="AI Model",
                        type="Model",
                        required=True,
                        description="AI model for the agent",
                    ),
                    InputDefinition(
                        name="knowledge",
                        display_name="Knowledge Base",
                        type="AgentKnowledge",
                        required=True,
                        description="Knowledge base for the agent",
                    ),
                    InputDefinition(
                        name="search_knowledge",
                        display_name="Enable Knowledge Search",
                        type="boolean",
                        required=False,
                        description="Enable knowledge base search",
                        default=True,
                    ),
                    InputDefinition(
                        name="tools",
                        display_name="Tools",
                        type="list",
                        required=False,
                        description="Additional tools for the agent",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="agent", display_name="Agent", type="Agent", description="Knowledge-enhanced agent"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_reasoning_agent",
                name="Reasoning Agent",
                display_name="Reasoning-Capable Agent",
                description="AI agent with advanced reasoning capabilities",
                category=ComponentCategory.AGENTS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="model",
                        display_name="AI Model",
                        type="Model",
                        required=True,
                        description="AI model for reasoning",
                    ),
                    InputDefinition(
                        name="reasoning_tools",
                        display_name="Reasoning Tools",
                        type="Toolkit",
                        required=True,
                        description="Reasoning toolkit for the agent",
                    ),
                    InputDefinition(
                        name="show_reasoning",
                        display_name="Show Reasoning",
                        type="boolean",
                        required=False,
                        description="Show reasoning steps to user",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="agent", display_name="Agent", type="Agent", description="Reasoning-capable agent"
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_team_components() -> List[ComponentMetadata]:
        """Get team components."""
        return [
            ComponentMetadata(
                id="agno_agent_team",
                name="Agent Team",
                display_name="Multi-Agent Team",
                description="Coordinated team of AI agents",
                category=ComponentCategory.TEAMS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="agents",
                        display_name="Team Members",
                        type="list",
                        required=True,
                        description="List of agents in the team",
                    ),
                    InputDefinition(
                        name="model",
                        display_name="Coordinator Model",
                        type="Model",
                        required=True,
                        description="Model for team coordination",
                    ),
                    InputDefinition(
                        name="mode",
                        display_name="Team Mode",
                        type="string",
                        required=False,
                        description="Team coordination mode",
                        default="coordinate",
                        options=["coordinate", "sequential", "parallel"],
                    ),
                    InputDefinition(
                        name="instructions",
                        display_name="Team Instructions",
                        type="list",
                        required=False,
                        description="Instructions for team coordination",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="team", display_name="Agent Team", type="Team", description="Configured agent team"
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_research_team",
                name="Research Team",
                display_name="Research Agent Team",
                description="Specialized team for research tasks",
                category=ComponentCategory.TEAMS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="research_agent",
                        display_name="Research Agent",
                        type="Agent",
                        required=True,
                        description="Agent specialized in research",
                    ),
                    InputDefinition(
                        name="analysis_agent",
                        display_name="Analysis Agent",
                        type="Agent",
                        required=True,
                        description="Agent specialized in analysis",
                    ),
                    InputDefinition(
                        name="writer_agent",
                        display_name="Writer Agent",
                        type="Agent",
                        required=True,
                        description="Agent specialized in writing",
                    ),
                    InputDefinition(
                        name="coordinator_model",
                        display_name="Coordinator Model",
                        type="Model",
                        required=True,
                        description="Model for coordinating the research team",
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="team", display_name="Research Team", type="Team", description="Research agent team"
                    )
                ],
                created_at=datetime.now(),
            ),
        ]

    @staticmethod
    def _get_workflow_components() -> List[ComponentMetadata]:
        """Get workflow components."""
        return [
            ComponentMetadata(
                id="agno_sequential_workflow",
                name="Sequential Workflow",
                display_name="Sequential Agent Workflow",
                description="Sequential execution workflow for agents",
                category=ComponentCategory.WORKFLOWS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="agents",
                        display_name="Workflow Agents",
                        type="list",
                        required=True,
                        description="Ordered list of agents for sequential execution",
                    ),
                    InputDefinition(
                        name="pass_results",
                        display_name="Pass Results Between Agents",
                        type="boolean",
                        required=False,
                        description="Pass results from one agent to the next",
                        default=True,
                    ),
                    InputDefinition(
                        name="stop_on_failure",
                        display_name="Stop on Failure",
                        type="boolean",
                        required=False,
                        description="Stop workflow if an agent fails",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="workflow",
                        display_name="Workflow",
                        type="Workflow",
                        description="Sequential agent workflow",
                    )
                ],
                created_at=datetime.now(),
            ),
            ComponentMetadata(
                id="agno_parallel_workflow",
                name="Parallel Workflow",
                display_name="Parallel Agent Workflow",
                description="Parallel execution workflow for agents",
                category=ComponentCategory.WORKFLOWS,
                framework=FrameworkType.AGNO,
                inputs=[
                    InputDefinition(
                        name="agents",
                        display_name="Workflow Agents",
                        type="list",
                        required=True,
                        description="List of agents for parallel execution",
                    ),
                    InputDefinition(
                        name="combine_results",
                        display_name="Combine Results",
                        type="boolean",
                        required=False,
                        description="Combine results from all agents",
                        default=True,
                    ),
                    InputDefinition(
                        name="wait_for_all",
                        display_name="Wait for All",
                        type="boolean",
                        required=False,
                        description="Wait for all agents to complete",
                        default=True,
                    ),
                ],
                outputs=[
                    OutputDefinition(
                        name="workflow", display_name="Workflow", type="Workflow", description="Parallel agent workflow"
                    )
                ],
                created_at=datetime.now(),
            ),
        ]
