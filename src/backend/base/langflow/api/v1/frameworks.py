"""API endpoints for framework management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from langflow.api.utils import CurrentActiveUser
from langflow.core.frameworks import get_framework_manager
from langflow.core.frameworks.exceptions import FrameworkError
from langflow.core.frameworks.types import ComponentMetadata, FrameworkType

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


@router.get("/{framework}/components", response_model=ComponentListResponse)
async def list_framework_components(
    framework: FrameworkType,
    _: CurrentActiveUser,
) -> ComponentListResponse:
    """List components available in a specific framework."""
    try:
        manager = get_framework_manager()

        # Initialize if not already done
        if not manager._initialized:
            await manager.initialize()

        if framework not in manager.get_available_frameworks():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework} is not available")

        components = await manager.get_all_components(framework_filter=framework)
        return ComponentListResponse(components=components)
    except HTTPException:
        raise
    except FrameworkError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list components for framework {framework}: {e!s}",
        ) from e


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
