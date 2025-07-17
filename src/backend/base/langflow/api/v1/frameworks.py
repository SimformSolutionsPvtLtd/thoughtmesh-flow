"""API endpoints for framework management."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from langflow.api.utils import CurrentActiveUser
from langflow.core.frameworks import get_framework_manager
from langflow.core.frameworks.exceptions import FrameworkError
from langflow.core.frameworks.types import ComponentMetadata, FrameworkType

router = APIRouter(prefix="/frameworks", tags=["Frameworks"])


class FrameworkStatusResponse(BaseModel):
    """Response model for framework status."""

    framework: str
    available: bool
    error: str | None = None


# Phase-4 API Models
class FrameworkInfo(BaseModel):
    """Detailed framework information model."""

    name: str = Field(..., description="Framework name")
    version: str = Field(..., description="Framework version")
    status: str = Field(..., description="Framework status (healthy/degraded/unhealthy)")
    component_count: int = Field(..., description="Number of available components")
    categories: list[str] = Field(default_factory=list, description="Available component categories")
    capabilities: list[str] = Field(default_factory=list, description="Framework capabilities")
    last_health_check: datetime | None = Field(default=None, description="Last health check timestamp")
    description: str | None = Field(default=None, description="Framework description")


class ComponentInfo(BaseModel):
    """Component information model."""

    id: str = Field(..., description="Component ID (framework:component_name)")
    name: str = Field(..., description="Component name")
    framework: str = Field(..., description="Source framework")
    category: str = Field(..., description="Component category")
    description: str = Field(..., description="Component description")
    status: str = Field(..., description="Component status")
    inputs: list[str] = Field(default_factory=list, description="Required inputs")
    outputs: list[str] = Field(default_factory=list, description="Available outputs")
    version: str = Field(default="1.0.0", description="Component version")
    dependencies: list[str] = Field(default_factory=list, description="Component dependencies")


class ComponentValidationRequest(BaseModel):
    """Component configuration validation request."""

    configuration: dict[str, Any] = Field(..., description="Component configuration")
    inputs: dict[str, Any] | None = Field(default=None, description="Input values for validation")


class ComponentTestRequest(BaseModel):
    """Component test execution request."""

    inputs: dict[str, Any] = Field(..., description="Test inputs")
    configuration: dict[str, Any] | None = Field(default=None, description="Component configuration")
    timeout: int | None = Field(default=30, description="Test timeout in seconds")


class FrameworkSwitchRequest(BaseModel):
    """Framework switching request."""

    component_mappings: dict[str, dict[str, str]] = Field(..., description="Component framework mappings")
    preserve_connections: bool = Field(default=True, description="Whether to preserve connections")
    validate_compatibility: bool = Field(default=True, description="Whether to validate compatibility")


class FlowExecutionRequest(BaseModel):
    """Enhanced flow execution request with framework preferences."""

    inputs: dict[str, Any] = Field(..., description="Flow inputs")
    framework_preferences: dict[str, str] | None = Field(default=None, description="Framework preferences")
    execution_options: dict[str, Any] | None = Field(default=None, description="Execution options")
    parallel_execution: bool = Field(default=False, description="Enable parallel execution")
    error_recovery: str = Field(default="standard", description="Error recovery strategy")
    monitoring: bool = Field(default=True, description="Enable monitoring")


class ComponentSearchResponse(BaseModel):
    """Component search response with pagination and filtering."""

    components: list[ComponentInfo]
    total: int
    limit: int
    offset: int
    filters: dict[str, Any] = Field(default_factory=dict)


class HealthCheckResponse(BaseModel):
    """Framework health check response."""

    framework: str
    status: str
    checks: dict[str, bool]
    timestamp: str


@router.get("/", response_model=list[FrameworkInfo])
async def list_frameworks(
    _: CurrentActiveUser,
) -> list[FrameworkInfo]:
    """List all available frameworks with detailed information."""
    try:
        manager = get_framework_manager()

        if not manager._initialized:
            await manager.initialize()

        frameworks = []
        for framework_name in manager.get_available_frameworks():
            try:
                adapter = manager.get_adapter(framework_name)
                components = await manager.get_all_components(framework_filter=framework_name)

                # Get categories from components
                categories = list({comp.category for comp in components if hasattr(comp, "category")})

                # Basic capabilities
                capabilities = ["component_discovery", "execution", "validation"]

                framework_info = FrameworkInfo(
                    name=framework_name,
                    version=getattr(adapter, "version", "1.0.0"),
                    status="healthy",  # TODO: Implement proper health checking
                    component_count=len(components),
                    categories=categories,
                    capabilities=capabilities,
                    last_health_check=datetime.now(),
                    description=f"{framework_name} framework integration",
                )
                frameworks.append(framework_info)
            except Exception as e:
                # Framework has issues, but still include it with error status
                framework_info = FrameworkInfo(
                    name=framework_name,
                    version="unknown",
                    status="unhealthy",
                    component_count=0,
                    categories=[],
                    capabilities=[],
                    description=f"Error: {e!s}",
                )
                frameworks.append(framework_info)

        return frameworks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list frameworks: {e!s}"
        ) from e


@router.get("/{framework}/components", response_model=ComponentSearchResponse)
async def list_framework_components(
    framework: FrameworkType,
    _: CurrentActiveUser,
) -> ComponentSearchResponse:
    """List components available in a specific framework."""
    try:
        manager = get_framework_manager()

        # Initialize if not already done
        if not manager._initialized:
            await manager.initialize()

        if framework not in manager.get_available_frameworks():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework} is not available")

        all_components = await manager.get_all_components(framework_filter=framework)

        # Convert to ComponentInfo format
        component_infos = []
        for comp in all_components:
            # Extract input and output names safely
            inputs = []
            if hasattr(comp, "inputs") and comp.inputs:
                if hasattr(comp.inputs, "keys"):
                    inputs = list(comp.inputs.keys())
                elif isinstance(comp.inputs, list):
                    inputs = [inp.name if hasattr(inp, "name") else str(inp) for inp in comp.inputs]
                else:
                    inputs = [str(comp.inputs)]

            outputs = []
            if hasattr(comp, "outputs") and comp.outputs:
                if hasattr(comp.outputs, "keys"):
                    outputs = list(comp.outputs.keys())
                elif isinstance(comp.outputs, list):
                    outputs = [out.name if hasattr(out, "name") else str(out) for out in comp.outputs]
                else:
                    outputs = [str(comp.outputs)]

            comp_info = ComponentInfo(
                id=f"{comp.framework if hasattr(comp, 'framework') else framework}:{comp.name}",
                name=comp.name,
                framework=comp.framework if hasattr(comp, "framework") else framework,
                category=comp.category if hasattr(comp, "category") else "unknown",
                description=comp.description if hasattr(comp, "description") else "No description",
                status="available",
                inputs=inputs,
                outputs=outputs,
                version=getattr(comp, "version", "1.0.0"),
                dependencies=getattr(comp, "dependencies", []),
            )
            component_infos.append(comp_info)

        return ComponentSearchResponse(
            components=component_infos,
            total=len(component_infos),
            limit=len(component_infos),
            offset=0,
            filters={"framework": framework},
        )
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

        return FrameworkStatusResponse(framework=str(framework), available=available, error=error)
    except FrameworkError as e:
        return FrameworkStatusResponse(framework=str(framework), available=False, error=str(e))


@router.get("/components", response_model=ComponentSearchResponse)
async def list_components(
    framework: str | None = None,
    category: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _: CurrentActiveUser = None,
) -> ComponentSearchResponse:
    """List components with filtering and pagination."""
    try:
        manager = get_framework_manager()

        if not manager._initialized:
            await manager.initialize()

        # Get components from specified framework or all frameworks
        if framework and framework != "all":
            if framework not in manager.get_available_frameworks():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework} not found")
            all_components = await manager.get_all_components(framework_filter=framework)
        else:
            all_components = await manager.get_all_components()

        # Convert to ComponentInfo format
        component_infos = []
        for comp in all_components:
            # Extract input and output names safely
            inputs = []
            if hasattr(comp, "inputs") and comp.inputs:
                if hasattr(comp.inputs, "keys"):
                    inputs = list(comp.inputs.keys())
                elif isinstance(comp.inputs, list):
                    inputs = [inp.name if hasattr(inp, "name") else str(inp) for inp in comp.inputs]
                else:
                    inputs = [str(comp.inputs)]

            outputs = []
            if hasattr(comp, "outputs") and comp.outputs:
                if hasattr(comp.outputs, "keys"):
                    outputs = list(comp.outputs.keys())
                elif isinstance(comp.outputs, list):
                    outputs = [out.name if hasattr(out, "name") else str(out) for out in comp.outputs]
                else:
                    outputs = [str(comp.outputs)]

            comp_info = ComponentInfo(
                id=f"{comp.framework if hasattr(comp, 'framework') else 'unknown'}:{comp.name}",
                name=comp.name,
                framework=comp.framework if hasattr(comp, "framework") else "unknown",
                category=comp.category if hasattr(comp, "category") else "unknown",
                description=comp.description if hasattr(comp, "description") else "No description",
                status="available",
                inputs=inputs,
                outputs=outputs,
                version=getattr(comp, "version", "1.0.0"),
                dependencies=getattr(comp, "dependencies", []),
            )
            component_infos.append(comp_info)

        # Apply filters
        filtered_components = component_infos

        if category and category != "all":
            filtered_components = [c for c in filtered_components if c.category == category]

        if search:
            search_lower = search.lower()
            filtered_components = [
                c
                for c in filtered_components
                if search_lower in c.name.lower() or search_lower in c.description.lower()
            ]

        # Apply pagination
        total = len(filtered_components)
        paginated = filtered_components[offset : offset + limit]

        return ComponentSearchResponse(
            components=paginated,
            total=total,
            limit=limit,
            offset=offset,
            filters={"framework": framework, "category": category, "search": search},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list components: {e!s}"
        ) from e


@router.get("/components/{component_id}")
async def get_component_details(
    component_id: str,
    _: CurrentActiveUser,
) -> dict[str, Any]:
    """Get detailed information about a specific component."""
    try:
        # Parse component_id (format: framework:component_name)
        if ":" not in component_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Component ID must be in format 'framework:component_name'",
            )

        framework_name, component_name = component_id.split(":", 1)

        manager = get_framework_manager()

        if not manager._initialized:
            await manager.initialize()

        if framework_name not in manager.get_available_frameworks():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework_name} not found")

        components = await manager.get_all_components(framework_filter=framework_name)

        # Find the specific component
        component = None
        for comp in components:
            if comp.name == component_name:
                component = comp
                break

        if not component:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Component {component_name} not found in {framework_name}",
            )

        # Return detailed component information
        return {
            "id": component_id,
            "name": component.name,
            "framework": framework_name,
            "category": getattr(component, "category", "unknown"),
            "description": getattr(component, "description", "No description"),
            "version": getattr(component, "version", "1.0.0"),
            "schema": {
                "inputs": getattr(component, "inputs", {}),
                "outputs": getattr(component, "outputs", {}),
                "configuration": getattr(component, "configuration_schema", {}),
            },
            "metadata": getattr(component, "metadata", {}),
            "dependencies": getattr(component, "dependencies", []),
            "examples": getattr(component, "examples", []),
            "status": "available",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get component details: {e!s}"
        ) from e


@router.post("/components/{component_id}/validate")
async def validate_component_config(
    component_id: str,
    request: ComponentValidationRequest,
    _: CurrentActiveUser,
) -> dict[str, Any]:
    """Validate component configuration."""
    try:
        # Parse component_id
        if ":" not in component_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Component ID must be in format 'framework:component_name'",
            )

        framework_name, component_name = component_id.split(":", 1)

        # For now, return a basic validation response
        # TODO: Implement proper validation logic with the framework manager
        return {"valid": True, "errors": [], "warnings": ["Validation implementation pending"], "suggestions": []}
    except HTTPException:
        raise
    except Exception as e:
        return {"valid": False, "errors": [f"Validation error: {e!s}"], "warnings": [], "suggestions": []}


@router.post("/components/{component_id}/test")
async def test_component_execution(
    component_id: str,
    request: ComponentTestRequest,
    _: CurrentActiveUser,
) -> dict[str, Any]:
    """Test component execution with provided inputs."""
    try:
        # Parse component_id
        if ":" not in component_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Component ID must be in format 'framework:component_name'",
            )

        framework_name, component_name = component_id.split(":", 1)

        # For now, return a basic test response
        # TODO: Implement proper component testing with the framework manager
        return {
            "success": True,
            "output": {"message": "Component test simulation - not yet implemented"},
            "error": None,
            "execution_time": 0.1,
            "mode": "simulation",
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "output": {},
            "error": f"Test execution failed: {e!s}",
            "execution_time": 0.0,
            "mode": "error",
        }


# =============================================================================
# Phase-4: Additional Framework Management Endpoints
# =============================================================================


@router.get("/{framework_name}", response_model=FrameworkInfo)
async def get_framework_details(
    framework_name: str,
    _: CurrentActiveUser,
) -> FrameworkInfo:
    """Get detailed information about a specific framework."""
    try:
        manager = get_framework_manager()

        if not manager._initialized:
            await manager.initialize()

        if framework_name not in manager.get_available_frameworks():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework_name} not found")

        adapter = manager.get_adapter(framework_name)
        components = await manager.get_all_components(framework_filter=framework_name)

        categories = list(set(comp.category for comp in components if hasattr(comp, "category")))
        capabilities = ["component_discovery", "execution", "validation"]

        return FrameworkInfo(
            name=framework_name,
            version=getattr(adapter, "version", "1.0.0"),
            status="healthy",  # TODO: Implement proper health checking
            component_count=len(components),
            categories=categories,
            capabilities=capabilities,
            last_health_check=datetime.now(),
            description=getattr(adapter, "description", f"{framework_name} framework integration"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get framework details: {str(e)}"
        ) from e


@router.post("/{framework_name}/health-check", response_model=HealthCheckResponse)
async def health_check_framework(
    framework_name: str,
    _: CurrentActiveUser,
) -> HealthCheckResponse:
    """Trigger a health check for a specific framework."""
    try:
        manager = get_framework_manager()

        if not manager._initialized:
            await manager.initialize()

        if framework_name not in manager.get_available_frameworks():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Framework {framework_name} not found")

        # Basic health checks
        adapter = manager.get_adapter(framework_name)
        components = await manager.get_all_components(framework_filter=framework_name)

        checks = {
            "adapter_loaded": True,
            "components_discoverable": len(components) > 0,
            "dependencies_satisfied": True,  # TODO: Implement proper dependency checking
        }

        overall_status = "healthy" if all(checks.values()) else "unhealthy"

        return HealthCheckResponse(
            framework=framework_name, status=overall_status, checks=checks, timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        return HealthCheckResponse(
            framework=framework_name, status="unhealthy", checks={"error": False}, timestamp=datetime.now().isoformat()
        )
