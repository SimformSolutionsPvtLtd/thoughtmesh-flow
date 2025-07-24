"""API endpoints for framework management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from langflow.api.utils import CurrentActiveUser
from langflow.core.frameworks import get_framework_manager
from langflow.core.frameworks.exceptions import FrameworkError
from langflow.core.frameworks.types import ComponentMetadata, FrameworkType
from langflow.utils.compression import compress_response

router = APIRouter(prefix="/frameworks", tags=["Frameworks"])


class FrameworkListResponse(BaseModel):
    """Response model for listing available frameworks."""

    frameworks: list[FrameworkType]


class ComponentListResponse(BaseModel):
    """Response model for listing framework components."""

    components: list[ComponentMetadata]


class FrameworkStatusResponse(BaseModel):
    """Response model for framework status."""

    framework: FrameworkType
    available: bool
    error: str | None = None


@router.get("/", response_model=FrameworkListResponse)
async def list_frameworks(
    _: CurrentActiveUser,
) -> FrameworkListResponse:
    """List all available frameworks."""
    try:
        manager = get_framework_manager()

        # Initialize if not already done
        if not manager._initialized:
            await manager.initialize()

        available_frameworks = list(manager.get_available_frameworks())
        return FrameworkListResponse(frameworks=available_frameworks)
    except FrameworkError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list frameworks: {e!s}"
        ) from e


@router.get("/{framework}/components")
async def list_framework_components(
    framework: FrameworkType,
    _: CurrentActiveUser,
):
    """List components available in a specific framework with same structure as /all endpoint."""
    try:
        manager = get_framework_manager()

        # Initialize if not already done
        if not manager._initialized:
            await manager.initialize()

        if framework not in manager.get_available_frameworks():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework} is not available")

        components = await manager.get_all_components(framework_filter=framework)
        
        # Convert to the same structure as /all endpoint
        categorized_components = _categorize_framework_components(components)
        return compress_response(categorized_components)
    except HTTPException:
        raise
    except FrameworkError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list components for framework {framework}: {e!s}",
        ) from e


def _categorize_framework_components(components: list[ComponentMetadata]) -> dict[str, dict[str, dict]]:
    """Categorize framework components to match /all endpoint structure."""
    # For framework-specific endpoints, organize by component category (Models, Tools, etc.)
    # to match the structure expected by frontend utilities
    
    categorized = {}
    
    for component in components:
        # Convert ComponentMetadata to the format expected by /all endpoint
        component_dict = _convert_component_metadata_to_all_format(component)
        
        # Skip components that couldn't be converted (invalid data)
        if component_dict is None:
            continue
        
        # Determine category for proper organization
        category_name = component.category or "models"  # Default to Models for agno components
        
        # For better categorization, let's use component names to determine categories
        if not component.category:
            display_name = component.display_name.lower()
            if any(keyword in display_name for keyword in ["tools", "search", "calculator", "file", "arxiv", "reasoning"]):
                category_name = "tools"
            elif any(keyword in display_name for keyword in ["vector", "database", "pgvector", "lancedb", "qdrant", "milvus", "pinecone"]):
                category_name = "vectorstores"
            elif any(keyword in display_name for keyword in ["knowledge", "pdf", "website", "document"]):
                category_name = "knowledge"
            elif any(keyword in display_name for keyword in ["embedding", "embedder"]):
                category_name = "embeddings"
            elif any(keyword in display_name for keyword in ["memory", "storage"]):
                category_name = "memory"
            elif any(keyword in display_name for keyword in ["rerank", "chunk"]):
                category_name = "processing"
            elif any(keyword in display_name for keyword in ["reader"]):
                category_name = "data"
            elif any(keyword in display_name for keyword in ["agent", "team", "workflow"]):
                category_name = "agents"
        
        print(f"Categorizing '{component.display_name}' as '{category_name}'")
        
        # Create category if it doesn't exist
        if category_name not in categorized:
            categorized[category_name] = {}
            
        # Add component to the appropriate category
        categorized[category_name][component.name] = component_dict
    
    print(f"Final categories: {categorized}")
    print(f"Final categories: {list(categorized.keys())}")
    print(f"Total components per category: {[(cat, len(comps)) for cat, comps in categorized.items()]}")
    
    return categorized


def _convert_component_metadata_to_all_format(component: ComponentMetadata) -> dict | None:
    """Convert ComponentMetadata to the format used by /all endpoint."""
    # Validate required fields
    if not component.display_name or not component.description:
        return None
    
    # Ensure inputs and outputs are not None
    inputs = component.inputs or []
    outputs = component.outputs or []
    tags = component.tags or []
    
    return {
        "template": {
            "_type": "Component",
            "display_name": component.display_name,
            "description": component.description,
            "documentation": "",
            "icon": component.icon or "Component",
            "framework": component.framework.value,
            "base_classes": ["BaseComponent"],
            "frozen": False,
            "custom_fields": {},
            "output_types": [],
            "pinned": False,
            "conditional_paths": [],
            "outputs": [
                {
                    "name": out.name,
                    "display_name": out.display_name,
                    "type": out.type,
                    "description": out.description,
                } for out in outputs if out.name and out.display_name
            ],
            "field_order": [inp.name for inp in inputs if inp.name],
            "beta": False,
            "legacy": False,
            "edited": False,
            "metadata": {},
            "tool_mode": False,
            **{
                inp.name: {
                    "tool_mode": False,
                    "trace_as_metadata": True,
                    "load_from_db": False,
                    "list": False,
                    "list_add_label": "Add More",
                    "required": inp.required if inp.required is not None else False,
                    "placeholder": "",
                    "show": True,
                    "name": inp.name,
                    "value": inp.default if inp.default is not None else "",
                    "display_name": inp.display_name or inp.name,
                    "advanced": False,
                    "dynamic": False,
                    "info": inp.description or "",
                    "title_case": False,
                    "type": inp.type or "str",
                    "_input_type": f"{(inp.type or 'str').title()}Input"
                } for inp in inputs if inp.name
            }
        },
        "description": component.description,
        "icon": component.icon or "Component",
        "base_classes": ["Tool"] if component.category == "Tools" else ["BaseComponent"],
        "display_name": component.display_name,
        "documentation": "",
        "minimized": False,
        "custom_fields": {},
        "output_types": [],
        "pinned": False,
        "conditional_paths": [],
        "frozen": False,
        "outputs": [
            {
                "name": out.name,
                "display_name": out.display_name,
                "type": out.type,
                "description": out.description,
            } for out in outputs if out.name and out.display_name
        ],
        "field_order": [inp.name for inp in inputs if inp.name],
        "beta": False,
        "legacy": False,
        "edited": False,
        "metadata": {},
        "tool_mode": False,
        "framework": component.framework.value,
        "framework_component_id": component.id,
        "lazy_loaded": False,
        "template_code": "",
        "field_config": {},
        "tags": tags,
        "version": component.version,
        "created_at": component.created_at.isoformat() if component.created_at else None,
        "updated_at": component.updated_at.isoformat() if component.updated_at else None,
    }


@router.get("/{framework}/status", response_model=FrameworkStatusResponse)
async def get_framework_status(
    framework: FrameworkType,
    _: CurrentActiveUser,
) -> FrameworkStatusResponse:
    """Get the status of a specific framework."""
    try:
        manager = get_framework_manager()

        # Initialize if not already done
        if not manager._initialized:
            await manager.initialize()

        available = framework in manager.get_available_frameworks()

        error = None
        if not available:
            # Try to get specific error information
            try:
                manager.get_adapter(framework)
            except FrameworkError as e:
                error = str(e)

        return FrameworkStatusResponse(framework=framework, available=available, error=error)
    except FrameworkError as e:
        return FrameworkStatusResponse(framework=framework, available=False, error=str(e))
