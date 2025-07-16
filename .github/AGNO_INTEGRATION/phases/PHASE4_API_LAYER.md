# Phase 4: API Layer Implementation (Week 7-8)

## 🎯 Objective
Implement comprehensive REST API layer for framework management, component discovery, and flow execution with framework switching capabilities.

## 📋 Prerequisites
- Phase 1-3 completed with core infrastructure and component system working
- Framework manager coordinating multiple adapters successfully
- Advanced workflow orchestration and monitoring operational
- Component registration and discovery systems functional

## 🌐 API Architecture

### 1. Framework Management Endpoints (`/api/v1/frameworks`)

#### Framework Discovery and Status
```python
# GET /api/v1/frameworks
# List all available frameworks
{
    "frameworks": [
        {
            "name": "agno",
            "version": "2.0.0",
            "status": "healthy",
            "component_count": 45,
            "categories": ["model", "tool", "vector_store", "agent"],
            "last_health_check": "2025-07-16T10:30:00Z"
        }
    ]
}

# GET /api/v1/frameworks/{framework_name}
# Get detailed framework information
{
    "name": "agno",
    "version": "2.0.0",
    "status": "healthy",
    "description": "Agno AI framework integration",
    "components": {...},
    "capabilities": [...],
    "configuration": {...}
}

# POST /api/v1/frameworks/{framework_name}/health-check
# Trigger framework health check
{
    "framework": "agno",
    "status": "healthy",
    "checks": {
        "adapter_loaded": true,
        "components_discoverable": true,
        "dependencies_satisfied": true
    },
    "timestamp": "2025-07-16T10:30:00Z"
}
```

#### Framework Configuration
```python
# GET /api/v1/frameworks/{framework_name}/config
# Get framework configuration
{
    "framework": "agno",
    "configuration": {
        "execution_mode": "real",
        "fallback_enabled": true,
        "performance_monitoring": true,
        "error_recovery": "intelligent"
    }
}

# PUT /api/v1/frameworks/{framework_name}/config
# Update framework configuration
{
    "configuration": {
        "execution_mode": "simulated",
        "fallback_enabled": false
    }
}
```

### 2. Component Discovery Endpoints (`/api/v1/components`)

#### Component Listing and Search
```python
# GET /api/v1/components
# List all components across frameworks
{
    "components": [
        {
            "id": "agno:openai_chat",
            "name": "openai_chat",
            "framework": "agno",
            "category": "model",
            "description": "OpenAI ChatGPT models",
            "status": "available",
            "inputs": ["messages", "model", "temperature"],
            "outputs": ["response", "usage"]
        }
    ],
    "total": 45,
    "filters": {...}
}

# GET /api/v1/components/search?q=openai&category=model&framework=agno
# Search components with filters
{
    "query": "openai",
    "results": [...],
    "facets": {
        "categories": {"model": 3, "tool": 1},
        "frameworks": {"agno": 4}
    }
}

# GET /api/v1/components/{component_id}
# Get detailed component information
{
    "id": "agno:openai_chat",
    "name": "openai_chat",
    "framework": "agno",
    "category": "model",
    "description": "OpenAI ChatGPT models",
    "version": "1.0.0",
    "schema": {
        "inputs": {...},
        "outputs": {...},
        "configuration": {...}
    },
    "metadata": {...},
    "dependencies": [...],
    "examples": [...]
}
```

#### Component Validation and Testing
```python
# POST /api/v1/components/{component_id}/validate
# Validate component configuration
{
    "configuration": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "api_key": "${OPENAI_API_KEY}"
    }
}

# Response
{
    "valid": true,
    "errors": [],
    "warnings": ["API key validation skipped in development mode"],
    "suggestions": []
}

# POST /api/v1/components/{component_id}/test
# Test component execution
{
    "inputs": {
        "messages": [{"role": "user", "content": "Hello!"}]
    },
    "configuration": {...}
}

# Response
{
    "success": true,
    "output": {...},
    "execution_time": 0.534,
    "mode": "real"
}
```

### 3. Flow Execution with Framework Support (`/api/v1/flows`)

#### Enhanced Flow Endpoints
```python
# POST /api/v1/flows/{flow_id}/run
# Execute flow with framework awareness
{
    "inputs": {...},
    "framework_preferences": {
        "agno": "preferred",
        "langflow": "fallback"
    },
    "execution_options": {
        "parallel_execution": true,
        "error_recovery": "intelligent",
        "monitoring": true
    }
}

# GET /api/v1/flows/{flow_id}/execution/{execution_id}
# Get flow execution status with framework details
{
    "execution_id": "exec_123",
    "status": "running",
    "progress": 0.65,
    "components": [
        {
            "component_id": "agno:openai_chat",
            "status": "completed",
            "framework": "agno",
            "execution_time": 0.234,
            "mode": "real"
        }
    ],
    "framework_usage": {
        "agno": {"components": 3, "execution_time": 0.845},
        "langflow": {"components": 2, "execution_time": 0.123}
    }
}
```

#### Framework Switching Logic
```python
# POST /api/v1/flows/{flow_id}/switch-framework
# Switch component frameworks in a flow
{
    "component_mappings": {
        "node_1": {
            "from": "langflow:text_input",
            "to": "agno:basic_agent"
        }
    },
    "preserve_connections": true,
    "validate_compatibility": true
}
```

### 4. Workflow Orchestration Endpoints (`/api/v1/workflows`)

#### Workflow Management
```python
# POST /api/v1/workflows
# Create new workflow
{
    "name": "AI Research Pipeline",
    "description": "Multi-step research workflow",
    "components": [...],
    "execution_strategy": "pipeline",
    "framework_requirements": {
        "agno": ["openai_chat", "duckduckgo_search"],
        "langflow": ["text_processor"]
    }
}

# GET /api/v1/workflows/{workflow_id}/execute
# Execute workflow with monitoring
{
    "execution_id": "wf_exec_456",
    "status": "running",
    "stages": [
        {
            "stage": "data_collection",
            "components": ["agno:duckduckgo_search"],
            "status": "completed"
        },
        {
            "stage": "analysis",
            "components": ["agno:openai_chat"],
            "status": "running"
        }
    ]
}
```

### 5. Performance Monitoring Endpoints (`/api/v1/monitoring`)

#### Performance Metrics
```python
# GET /api/v1/monitoring/performance
# Get performance metrics
{
    "summary": {
        "total_executions": 1520,
        "success_rate": 0.987,
        "average_execution_time": 0.423,
        "frameworks": {
            "agno": {"executions": 1100, "success_rate": 0.991},
            "langflow": {"executions": 420, "success_rate": 0.978}
        }
    },
    "components": [...],
    "trends": [...]
}

# GET /api/v1/monitoring/health
# Get system health status
{
    "overall_status": "healthy",
    "frameworks": [...],
    "components": [...],
    "system_resources": {...},
    "alerts": []
}
```

## 🏗️ Implementation Structure

### 1. API Router Setup (`api/v1/frameworks/router.py`)

```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from ...core.frameworks import framework_manager
from .schemas import FrameworkInfo, ComponentInfo, ExecutionRequest

router = APIRouter(prefix="/frameworks", tags=["frameworks"])

@router.get("/", response_model=List[FrameworkInfo])
async def list_frameworks():
    """List all available frameworks"""
    adapters_info = framework_manager.get_adapters_info()
    return [
        FrameworkInfo(
            name=name,
            version=info["version"],
            status="healthy" if info["healthy"] else "unhealthy",
            component_count=info["component_count"]
        )
        for name, info in adapters_info.items()
    ]

@router.get("/{framework_name}", response_model=FrameworkInfo)
async def get_framework(framework_name: str):
    """Get detailed framework information"""
    if framework_name not in framework_manager._adapters:
        raise HTTPException(404, f"Framework {framework_name} not found")
    
    adapter = framework_manager._adapters[framework_name]
    components = await adapter.discover_components()
    
    return FrameworkInfo(
        name=adapter.name,
        version=adapter.version,
        status="healthy" if await adapter.health_check() else "unhealthy",
        component_count=len(components),
        components=[ComponentInfo.from_component_info(comp) for comp in components]
    )

@router.post("/{framework_name}/health-check")
async def health_check_framework(framework_name: str):
    """Trigger framework health check"""
    if framework_name not in framework_manager._adapters:
        raise HTTPException(404, f"Framework {framework_name} not found")
    
    adapter = framework_manager._adapters[framework_name]
    health_status = await adapter.health_check()
    
    return {
        "framework": framework_name,
        "status": "healthy" if health_status else "unhealthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 2. Component Discovery Router (`api/v1/components/router.py`)

```python
@router.get("/", response_model=ComponentListResponse)
async def list_components(
    framework: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List components with filtering and pagination"""
    all_components = framework_manager.get_all_components()
    
    # Apply filters
    filtered_components = []
    for comp in all_components.values():
        if framework and comp.framework != framework:
            continue
        if category and comp.category.value != category:
            continue
        if search and search.lower() not in comp.name.lower() and search.lower() not in comp.description.lower():
            continue
        
        filtered_components.append(comp)
    
    # Apply pagination
    total = len(filtered_components)
    paginated = filtered_components[offset:offset + limit]
    
    return ComponentListResponse(
        components=[ComponentInfo.from_component_info(comp) for comp in paginated],
        total=total,
        limit=limit,
        offset=offset
    )

@router.post("/{component_id}/validate")
async def validate_component_config(
    component_id: str,
    config: Dict[str, Any]
):
    """Validate component configuration"""
    # Parse component_id (format: framework:component_name)
    if ":" not in component_id:
        raise HTTPException(400, "Component ID must be in format 'framework:component_name'")
    
    framework_name, component_name = component_id.split(":", 1)
    
    validation_result = await framework_manager.validate_component(component_name, config)
    
    return {
        "valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "suggestions": validation_result.suggestions
    }

@router.post("/{component_id}/test")
async def test_component_execution(
    component_id: str,
    request: ComponentTestRequest
):
    """Test component execution"""
    framework_name, component_name = component_id.split(":", 1)
    
    result = await framework_manager.execute_component(
        component_name,
        request.inputs,
        request.configuration or {}
    )
    
    return {
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "execution_time": result.execution_time,
        "mode": result.mode.value
    }
```

### 3. Enhanced Flow Execution (`api/v1/flows/router.py`)

```python
@router.post("/{flow_id}/run")
async def run_flow_with_frameworks(
    flow_id: str,
    request: FlowExecutionRequest
):
    """Execute flow with framework awareness"""
    
    # Get flow definition
    flow = await get_flow_by_id(flow_id)
    if not flow:
        raise HTTPException(404, "Flow not found")
    
    # Create execution context with framework preferences
    execution_context = FlowExecutionContext(
        flow_id=flow_id,
        framework_preferences=request.framework_preferences,
        execution_options=request.execution_options,
        inputs=request.inputs
    )
    
    # Execute flow through enhanced flow runner
    execution_id = await enhanced_flow_runner.execute(execution_context)
    
    return {"execution_id": execution_id, "status": "started"}

@router.get("/{flow_id}/execution/{execution_id}")
async def get_flow_execution_status(flow_id: str, execution_id: str):
    """Get detailed execution status with framework information"""
    
    execution = await get_execution_by_id(execution_id)
    if not execution:
        raise HTTPException(404, "Execution not found")
    
    # Get framework-specific execution details
    framework_usage = {}
    for component_result in execution.component_results:
        framework = component_result.framework
        if framework not in framework_usage:
            framework_usage[framework] = {
                "components": 0,
                "execution_time": 0.0,
                "success_count": 0,
                "error_count": 0
            }
        
        framework_usage[framework]["components"] += 1
        framework_usage[framework]["execution_time"] += component_result.execution_time
        
        if component_result.success:
            framework_usage[framework]["success_count"] += 1
        else:
            framework_usage[framework]["error_count"] += 1
    
    return {
        "execution_id": execution_id,
        "status": execution.status,
        "progress": execution.progress,
        "components": execution.component_results,
        "framework_usage": framework_usage,
        "start_time": execution.start_time,
        "end_time": execution.end_time
    }
```

### 4. Workflow Orchestration API (`api/v1/workflows/router.py`)

```python
@router.post("/")
async def create_workflow(workflow_def: WorkflowDefinition):
    """Create new workflow with framework requirements"""
    
    # Validate workflow definition
    validation_result = await workflow_engine.validate_workflow(workflow_def)
    if not validation_result.is_valid:
        raise HTTPException(400, f"Invalid workflow: {validation_result.errors}")
    
    # Register workflow
    workflow_id = await workflow_engine.register_workflow(workflow_def)
    
    return {"workflow_id": workflow_id, "status": "registered"}

@router.post("/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    inputs: Dict[str, Any]
):
    """Execute registered workflow"""
    
    execution_id = await workflow_engine.execute_workflow(workflow_id, inputs)
    
    return {"execution_id": execution_id, "status": "started"}

@router.get("/{workflow_id}/execution/{execution_id}")
async def get_workflow_execution(workflow_id: str, execution_id: str):
    """Get workflow execution status"""
    
    status = workflow_engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(404, "Execution not found")
    
    return status
```

## 📊 API Documentation and Testing

### 1. OpenAPI Schema Generation
```python
# Add to main FastAPI app
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Langflow Framework Integration API",
        version="2.0.0",
        description="Comprehensive API for multi-framework AI component orchestration",
        routes=app.routes,
    )
    
    # Add framework-specific documentation
    openapi_schema["info"]["x-framework-support"] = {
        "agno": "Full integration with 45+ components",
        "langflow": "Native Langflow components",
        "extensible": "Plugin architecture for additional frameworks"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 2. API Testing Suite
```python
# tests/api/test_frameworks.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_frameworks(client: AsyncClient):
    """Test framework listing endpoint"""
    response = await client.get("/api/v1/frameworks/")
    assert response.status_code == 200
    
    frameworks = response.json()
    assert isinstance(frameworks, list)
    assert len(frameworks) > 0
    
    # Check for agno framework
    agno_framework = next((f for f in frameworks if f["name"] == "agno"), None)
    assert agno_framework is not None
    assert agno_framework["component_count"] >= 45

@pytest.mark.asyncio
async def test_component_discovery(client: AsyncClient):
    """Test component discovery and search"""
    # Test basic listing
    response = await client.get("/api/v1/components/")
    assert response.status_code == 200
    
    components = response.json()["components"]
    assert len(components) > 0
    
    # Test search functionality
    search_response = await client.get("/api/v1/components/?search=openai")
    assert search_response.status_code == 200
    
    search_results = search_response.json()["components"]
    assert all("openai" in comp["name"].lower() or "openai" in comp["description"].lower() 
              for comp in search_results)

@pytest.mark.asyncio
async def test_component_validation(client: AsyncClient):
    """Test component configuration validation"""
    validation_data = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = await client.post(
        "/api/v1/components/agno:openai_chat/validate",
        json=validation_data
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["valid"] is True
    assert isinstance(result["errors"], list)
```

## 📋 Implementation Checklist

### Core API Development
- [ ] Implement framework management endpoints
- [ ] Create component discovery and search APIs
- [ ] Add component validation and testing endpoints
- [ ] Enhance flow execution with framework support
- [ ] Implement workflow orchestration APIs

### Framework Integration
- [ ] Add framework switching logic in flows
- [ ] Implement framework preference system
- [ ] Create framework-aware execution context
- [ ] Add framework performance tracking
- [ ] Implement framework health monitoring

### API Features
- [ ] Add comprehensive input validation
- [ ] Implement rate limiting and authentication
- [ ] Add API versioning support
- [ ] Create detailed error responses
- [ ] Add request/response logging

### Documentation and Testing
- [ ] Generate comprehensive OpenAPI schemas
- [ ] Create API usage examples and tutorials
- [ ] Add comprehensive test coverage
- [ ] Implement API performance testing
- [ ] Create API integration guides

## 🎯 Success Criteria

### Functionality
- ✅ All framework operations accessible via REST API
- ✅ Component discovery and management fully functional
- ✅ Flow execution with framework switching working
- ✅ Workflow orchestration APIs operational
- ✅ Real-time monitoring and status endpoints active

### Performance
- ✅ API response times <200ms for simple operations
- ✅ Component discovery APIs handle 100+ concurrent requests
- ✅ Flow execution APIs support long-running operations
- ✅ Efficient pagination and filtering for large datasets
- ✅ Proper caching for frequently accessed data

### Integration Quality
- ✅ Seamless integration with existing Langflow APIs
- ✅ Backward compatibility with current flow execution
- ✅ Framework-agnostic API design
- ✅ Comprehensive error handling and user feedback
- ✅ Production-ready authentication and authorization

---

**🎯 Phase 4 Goal**: Provide comprehensive REST API access to all framework integration features, enabling programmatic control of multi-framework AI workflows through well-designed, documented, and tested endpoints.
