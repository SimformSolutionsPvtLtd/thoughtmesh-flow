#!/usr/bin/env python3
"""
Test script to validate Agno components without full environment
"""

import os
import sys
from typing import Any, Dict, List


# Mock the dependencies to allow import without full environment
class MockBaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockField:
    def __init__(self, *args, **kwargs):
        pass


# Mock pydantic
sys.modules["pydantic"] = type("Module", (), {"BaseModel": MockBaseModel, "Field": MockField})
sys.modules["pydantic.v1"] = type("Module", (), {"BaseModel": MockBaseModel, "Field": MockField})

# Add the source path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src/backend/base"))

# Mock the types we need
from datetime import datetime
from enum import Enum


class ComponentCategory(str, Enum):
    """Component categories"""

    TOOLS = "Tools"
    MODELS = "Models"
    VECTOR_STORES = "Vector Stores"
    KNOWLEDGE_BASES = "Knowledge Bases"
    EMBEDDINGS = "Embeddings"
    RETRIEVERS = "Retrievers"
    MEMORY = "Memory"
    STORAGE = "Storage"
    RERANKERS = "Rerankers"
    CHUNKING = "Chunking"
    DOCUMENT_READERS = "Document Readers"
    CHAINS = "Chains"
    AGENTS = "Agents"
    TEAMS = "Teams"
    WORKFLOWS = "Workflows"
    UTILITIES = "Utilities"


class FrameworkType(str, Enum):
    """Supported framework types"""

    LANGFLOW = "langflow"
    AGNO = "agno"


class InputDefinition:
    """Definition for component input"""

    def __init__(self, name, display_name, type, required=False, description="", default=None, **kwargs):
        self.name = name
        self.display_name = display_name
        self.type = type
        self.required = required
        self.description = description
        self.default = default
        for k, v in kwargs.items():
            setattr(self, k, v)


class OutputDefinition:
    """Definition for component output"""

    def __init__(self, name, display_name, type, description=""):
        self.name = name
        self.display_name = display_name
        self.type = type
        self.description = description


class ComponentMetadata:
    """Metadata for a framework component"""

    def __init__(self, id, name, display_name, description="", category=None, framework=None, **kwargs):
        self.id = id
        self.name = name
        self.display_name = display_name
        self.description = description
        self.category = category
        self.framework = framework
        self.inputs = kwargs.get("inputs", [])
        self.outputs = kwargs.get("outputs", [])
        self.created_at = kwargs.get("created_at", datetime.now())
        for k, v in kwargs.items():
            if k not in ["inputs", "outputs", "created_at"]:
                setattr(self, k, v)


# Now try to import and test the components
try:
    # Mock the types module
    import langflow.core.frameworks.types

    langflow.core.frameworks.types.ComponentCategory = ComponentCategory
    langflow.core.frameworks.types.FrameworkType = FrameworkType
    langflow.core.frameworks.types.InputDefinition = InputDefinition
    langflow.core.frameworks.types.OutputDefinition = OutputDefinition
    langflow.core.frameworks.types.ComponentMetadata = ComponentMetadata

    from langflow.core.frameworks.agno_components import AgnoComponentRegistry

    print("Successfully imported AgnoComponentRegistry")

    # Test component retrieval
    components = AgnoComponentRegistry.get_all_components()
    print(f"Found {len(components)} components")

    # Check each component for required fields
    issues = []
    for i, component in enumerate(components):
        if not hasattr(component, "name") or not component.name:
            issues.append(f"Component {i}: missing name (id: {getattr(component, 'id', 'unknown')})")
        if not hasattr(component, "display_name") or not component.display_name:
            issues.append(f"Component {i}: missing display_name (id: {getattr(component, 'id', 'unknown')})")
        if not hasattr(component, "description") or not component.description:
            issues.append(f"Component {i}: missing description (id: {getattr(component, 'id', 'unknown')})")
        if not hasattr(component, "framework") or not component.framework:
            issues.append(f"Component {i}: missing framework (id: {getattr(component, 'id', 'unknown')})")

    if issues:
        print(f"\nFound {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nAll components have required fields!")

    # Sample a few components
    print(f"\nFirst 3 components:")
    for i, component in enumerate(components[:3]):
        print(f"  {i + 1}. {component.name} ({component.id}) - {component.display_name}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
