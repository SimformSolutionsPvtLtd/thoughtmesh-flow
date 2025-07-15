from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for environments where pydantic v1 is used
    from pydantic.v1 import BaseModel, Field


class FrameworkType(str, Enum):
    """Supported framework types"""

    LANGFLOW = "langflow"
    AGNO = "agno"


class ComponentCategory(str, Enum):
    """Component categories"""

    TOOLS = "Tools"
    MODELS = "Models"
    VECTOR_STORES = "Vector Stores"
    KNOWLEDGE_BASES = "Knowledge Bases"
    EMBEDDINGS = "Embeddings"
    RETRIEVERS = "Retrievers"
    MEMORY = "Memory"
    CHAINS = "Chains"
    AGENTS = "Agents"
    UTILITIES = "Utilities"


class InputDefinition(BaseModel):
    """Definition for component input"""

    name: str = Field(..., description="Input parameter name")
    display_name: str = Field(..., description="Human-readable display name")
    type: str = Field(..., description="Input data type")
    required: bool = Field(default=False, description="Whether input is required")
    description: str = Field("", description="Input description")
    default: Any | None = Field(None, description="Default value")
    options: list[str] | None = Field(None, description="Available options for select inputs")
    min_value: int | float | None = Field(None, description="Minimum value for numeric inputs")
    max_value: int | float | None = Field(None, description="Maximum value for numeric inputs")


class OutputDefinition(BaseModel):
    """Definition for component output"""

    name: str = Field(..., description="Output parameter name")
    display_name: str = Field(..., description="Human-readable display name")
    type: str = Field(..., description="Output data type")
    description: str = Field("", description="Output description")


class ComponentMetadata(BaseModel):
    """Metadata for a framework component"""

    id: str = Field(..., description="Unique component identifier")
    name: str = Field(..., description="Component name")
    display_name: str = Field(..., description="Human-readable display name")
    description: str = Field("", description="Component description")
    category: ComponentCategory = Field(..., description="Component category")
    framework: FrameworkType = Field(..., description="Source framework")
    version: str = Field("1.0.0", description="Component version")
    icon: str | None = Field(None, description="Component icon")
    inputs: list[InputDefinition] = Field(default_factory=list, description="Input definitions")
    outputs: list[OutputDefinition] = Field(default_factory=list, description="Output definitions")
    config_schema: dict[str, Any] = Field(default_factory=dict, description="Configuration schema")
    tags: list[str] = Field(default_factory=list, description="Component tags")
    documentation_url: str | None = Field(None, description="Link to component documentation")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class ExecutionContext(BaseModel):
    """Context for component execution"""

    component_id: str
    inputs: dict[str, Any]
    config: dict[str, Any]
    session_id: str | None = None
    user_id: str | None = None
    flow_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of component execution"""

    success: bool = Field(..., description="Whether execution was successful")
    data: Any = Field(None, description="Execution result data")
    error: str | None = Field(None, description="Error message if execution failed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    execution_time: float | None = Field(None, description="Execution time in seconds")
    framework: FrameworkType = Field(..., description="Framework that executed the component")
