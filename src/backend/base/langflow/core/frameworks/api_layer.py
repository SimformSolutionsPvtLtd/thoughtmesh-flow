"""
REST API Layer for Agno Framework Integration.

This module provides comprehensive REST API endpoints, middleware,
authentication, and documentation for the Langflow-Agno integration.
"""

import asyncio
import json
import logging
import time
from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GzipMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

    # Fallback classes for type hints
    class BaseModel:
        pass

    class HTTPException(Exception):
        pass


logger = logging.getLogger(__name__)


class APIStatus(Enum):
    """API status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class PermissionLevel(Enum):
    """Permission levels for API access."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class APIMetrics:
    """API metrics tracking."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_response_time: float = 0.0
    active_connections: int = 0
    rate_limited_requests: int = 0
    last_request_time: Optional[datetime] = None


class RateLimiter:
    """Simple rate limiting implementation."""

    def __init__(self, requests_per_minute: int = 60, window_minutes: int = 1):
        self.requests_per_minute = requests_per_minute
        self.window_minutes = window_minutes
        self.requests: Dict[str, List[datetime]] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limits."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.window_minutes)

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [req_time for req_time in self.requests[client_id] if req_time > cutoff]
        else:
            self.requests[client_id] = []

        # Check if under limit
        if len(self.requests[client_id]) < self.requests_per_minute:
            self.requests[client_id].append(now)
            return True

        return False


# Pydantic models for API requests/responses
if FASTAPI_AVAILABLE:

    class BaseAPIModel(BaseModel):
        """Base model for API requests/responses."""

        class Config:
            arbitrary_types_allowed = True
            json_encoders = {datetime: lambda v: v.isoformat()}

    class HealthResponse(BaseAPIModel):
        """Health check response model."""

        status: str = Field(..., description="API health status")
        timestamp: datetime = Field(default_factory=datetime.now)
        version: str = Field(..., description="API version")
        uptime: float = Field(..., description="Uptime in seconds")
        metrics: Dict[str, Any] = Field(default_factory=dict)

    class AgnoJobRequest(BaseAPIModel):
        """Request model for Agno job submission."""

        workflow_id: str = Field(..., description="Workflow identifier")
        input_data: Dict[str, Any] = Field(..., description="Input data for processing")
        config: Optional[Dict[str, Any]] = Field(None, description="Job configuration")
        priority: int = Field(1, ge=1, le=10, description="Job priority (1-10)")
        timeout: Optional[int] = Field(None, description="Job timeout in seconds")
        metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class AgnoJobResponse(BaseAPIModel):
        """Response model for Agno job submission."""

        job_id: str = Field(..., description="Unique job identifier")
        status: str = Field(..., description="Job status")
        submitted_at: datetime = Field(default_factory=datetime.now)
        estimated_completion: Optional[datetime] = Field(None)
        message: str = Field("", description="Status message")

    class AgnoJobStatus(BaseAPIModel):
        """Model for Agno job status."""

        job_id: str
        status: str
        progress: float = Field(ge=0.0, le=1.0, description="Job progress (0-1)")
        result: Optional[Dict[str, Any]] = None
        error: Optional[str] = None
        started_at: Optional[datetime] = None
        completed_at: Optional[datetime] = None
        runtime_seconds: Optional[float] = None

    class WorkflowCreateRequest(BaseAPIModel):
        """Request model for workflow creation."""

        name: str = Field(..., description="Workflow name")
        description: Optional[str] = Field(None, description="Workflow description")
        components: List[Dict[str, Any]] = Field(..., description="Workflow components")
        connections: List[Dict[str, Any]] = Field(..., description="Component connections")
        config: Optional[Dict[str, Any]] = Field(None, description="Workflow configuration")
        tags: Optional[List[str]] = Field(None, description="Workflow tags")

    class WorkflowResponse(BaseAPIModel):
        """Response model for workflow operations."""

        workflow_id: str
        name: str
        description: Optional[str] = None
        status: str
        created_at: datetime
        updated_at: datetime
        version: int = 1
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class ErrorResponse(BaseAPIModel):
        """Standard error response model."""

        error: str = Field(..., description="Error type")
        message: str = Field(..., description="Error message")
        details: Optional[Dict[str, Any]] = Field(None, description="Error details")
        timestamp: datetime = Field(default_factory=datetime.now)
        request_id: Optional[str] = Field(None, description="Request identifier")


class AgnoAPIRouter:
    """REST API router for Agno framework integration."""

    def __init__(self, app: Optional[Any] = None):
        self.app = app
        self.metrics = APIMetrics()
        self.rate_limiter = RateLimiter()
        self.start_time = datetime.now()
        self.security = HTTPBearer() if FASTAPI_AVAILABLE else None

        # Mock data stores (replace with actual implementations)
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.active_jobs: Dict[str, Any] = {}

        if FASTAPI_AVAILABLE and app:
            self._setup_routes()
            self._setup_middleware()

    def _setup_middleware(self):
        """Setup API middleware."""
        if not self.app:
            return

        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Gzip middleware
        self.app.add_middleware(GzipMiddleware, minimum_size=1000)

        # Custom middleware for metrics and rate limiting
        @self.app.middleware("http")
        async def metrics_middleware(request: Request, call_next: Callable) -> Response:
            start_time = time.time()

            # Rate limiting
            client_ip = request.client.host
            if not self.rate_limiter.is_allowed(client_ip):
                self.metrics.rate_limited_requests += 1
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

            # Process request
            try:
                response = await call_next(request)
                self.metrics.successful_requests += 1
            except Exception as e:
                self.metrics.failed_requests += 1
                logger.error(f"Request failed: {e}")
                raise
            finally:
                # Update metrics
                response_time = time.time() - start_time
                self.metrics.total_requests += 1
                self.metrics.last_request_time = datetime.now()

                # Update average response time
                if self.metrics.total_requests == 1:
                    self.metrics.average_response_time = response_time
                else:
                    self.metrics.average_response_time = (
                        self.metrics.average_response_time * (self.metrics.total_requests - 1) + response_time
                    ) / self.metrics.total_requests

                # Update peak response time
                if response_time > self.metrics.peak_response_time:
                    self.metrics.peak_response_time = response_time

            return response

    def _setup_routes(self):
        """Setup API routes."""
        if not self.app:
            return

        # Health check endpoint
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            uptime = (datetime.now() - self.start_time).total_seconds()

            health_status = APIStatus.HEALTHY.value
            if self.metrics.failed_requests > self.metrics.successful_requests * 0.1:
                health_status = APIStatus.DEGRADED.value

            metrics = {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (self.metrics.successful_requests / max(self.metrics.total_requests, 1)),
                "average_response_time": self.metrics.average_response_time,
                "peak_response_time": self.metrics.peak_response_time,
                "active_connections": self.metrics.active_connections,
            }

            return HealthResponse(status=health_status, version="1.0.0", uptime=uptime, metrics=metrics)

        # Workflow management endpoints
        @self.app.post("/workflows", response_model=WorkflowResponse)
        async def create_workflow(
            request: WorkflowCreateRequest, credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Create a new workflow."""
            # Validate authentication (implement actual auth logic)
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            workflow_id = f"wf_{int(time.time())}"
            workflow_data = {
                "workflow_id": workflow_id,
                "name": request.name,
                "description": request.description,
                "components": request.components,
                "connections": request.connections,
                "config": request.config or {},
                "tags": request.tags or [],
                "status": "created",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "version": 1,
                "metadata": {},
            }

            self.workflows[workflow_id] = workflow_data

            return WorkflowResponse(**workflow_data)

        @self.app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
        async def get_workflow(workflow_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Get workflow by ID."""
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            if workflow_id not in self.workflows:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found")

            return WorkflowResponse(**self.workflows[workflow_id])

        @self.app.get("/workflows", response_model=List[WorkflowResponse])
        async def list_workflows(
            limit: int = 50, offset: int = 0, credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """List workflows with pagination."""
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            workflows = list(self.workflows.values())
            paginated = workflows[offset : offset + limit]

            return [WorkflowResponse(**wf) for wf in paginated]

        # Job management endpoints
        @self.app.post("/jobs", response_model=AgnoJobResponse)
        async def submit_job(
            request: AgnoJobRequest, credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Submit a new Agno job."""
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            # Validate workflow exists
            if request.workflow_id not in self.workflows:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {request.workflow_id} not found"
                )

            job_id = f"job_{int(time.time())}"
            job_data = {
                "job_id": job_id,
                "workflow_id": request.workflow_id,
                "status": "submitted",
                "input_data": request.input_data,
                "config": request.config or {},
                "priority": request.priority,
                "timeout": request.timeout,
                "metadata": request.metadata or {},
                "submitted_at": datetime.now(),
                "progress": 0.0,
                "result": None,
                "error": None,
                "started_at": None,
                "completed_at": None,
            }

            self.jobs[job_id] = job_data

            # Start job processing (mock implementation)
            asyncio.create_task(self._process_job(job_id))

            estimated_completion = None
            if request.timeout:
                estimated_completion = datetime.now() + timedelta(seconds=request.timeout)

            return AgnoJobResponse(
                job_id=job_id,
                status="submitted",
                estimated_completion=estimated_completion,
                message="Job submitted successfully",
            )

        @self.app.get("/jobs/{job_id}", response_model=AgnoJobStatus)
        async def get_job_status(job_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Get job status by ID."""
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            if job_id not in self.jobs:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found")

            job_data = self.jobs[job_id]

            # Calculate runtime if job has started
            runtime_seconds = None
            if job_data["started_at"]:
                end_time = job_data["completed_at"] or datetime.now()
                runtime_seconds = (end_time - job_data["started_at"]).total_seconds()

            return AgnoJobStatus(
                job_id=job_id,
                status=job_data["status"],
                progress=job_data["progress"],
                result=job_data["result"],
                error=job_data["error"],
                started_at=job_data["started_at"],
                completed_at=job_data["completed_at"],
                runtime_seconds=runtime_seconds,
            )

        @self.app.delete("/jobs/{job_id}")
        async def cancel_job(job_id: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Cancel a running job."""
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            if job_id not in self.jobs:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found")

            job_data = self.jobs[job_id]

            if job_data["status"] in ["completed", "failed", "cancelled"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel job in {job_data['status']} state"
                )

            # Cancel the job
            job_data["status"] = "cancelled"
            job_data["completed_at"] = datetime.now()

            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

            return {"message": f"Job {job_id} cancelled successfully"}

        # Metrics endpoint
        @self.app.get("/metrics")
        async def get_metrics(credentials: HTTPAuthorizationCredentials = Depends(self.security)):
            """Get API metrics."""
            if not self._validate_token(credentials.credentials):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

            uptime = (datetime.now() - self.start_time).total_seconds()

            return {
                "uptime_seconds": uptime,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": (self.metrics.successful_requests / max(self.metrics.total_requests, 1)),
                "average_response_time": self.metrics.average_response_time,
                "peak_response_time": self.metrics.peak_response_time,
                "active_connections": self.metrics.active_connections,
                "rate_limited_requests": self.metrics.rate_limited_requests,
                "active_jobs": len(self.active_jobs),
                "total_workflows": len(self.workflows),
                "total_jobs": len(self.jobs),
                "last_request_time": self.metrics.last_request_time.isoformat()
                if self.metrics.last_request_time
                else None,
            }

    def _validate_token(self, token: str) -> bool:
        """Validate authentication token (implement actual validation)."""
        # Mock validation - implement actual JWT/OAuth validation
        return token.startswith("agno_") or token == "dev_token"

    async def _process_job(self, job_id: str):
        """Mock job processing (replace with actual Agno integration)."""
        if job_id not in self.jobs:
            return

        job_data = self.jobs[job_id]
        self.active_jobs[job_id] = job_data

        try:
            # Mark as started
            job_data["status"] = "running"
            job_data["started_at"] = datetime.now()

            # Simulate processing with progress updates
            for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
                await asyncio.sleep(2)  # Simulate work

                if job_data["status"] == "cancelled":
                    return

                job_data["progress"] = progress

            # Mark as completed
            job_data["status"] = "completed"
            job_data["completed_at"] = datetime.now()
            job_data["result"] = {"output": "Mock processing result", "processed_items": 100, "success": True}

        except Exception as e:
            # Mark as failed
            job_data["status"] = "failed"
            job_data["completed_at"] = datetime.now()
            job_data["error"] = str(e)
            logger.error(f"Job {job_id} failed: {e}")

        finally:
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]


def create_agno_api_app() -> Optional[Any]:
    """Create FastAPI application with Agno integration."""
    if not FASTAPI_AVAILABLE:
        logger.warning("FastAPI not available. REST API features disabled.")
        return None

    app = FastAPI(
        title="Langflow Agno Integration API",
        description="REST API for Langflow-Agno framework integration",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Initialize router
    router = AgnoAPIRouter(app)

    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {exc}")

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An internal server error occurred",
                "timestamp": datetime.now().isoformat(),
            },
        )

    return app


# Global API app instance
api_app = create_agno_api_app()


# Utility functions
def start_api_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Start the API server."""
    if not FASTAPI_AVAILABLE:
        logger.error("Cannot start API server: FastAPI not available")
        return

    try:
        import uvicorn

        uvicorn.run(api_app, host=host, port=port, debug=debug)
    except ImportError:
        logger.error("Cannot start API server: uvicorn not available")


def get_api_client():
    """Get API client for making requests."""
    # This would return a configured HTTP client for making API requests
    # Implementation depends on preferred HTTP client library
    pass


# API decorators for framework integration
def api_endpoint(path: str, methods: List[str] = None):
    """Decorator for registering API endpoints."""
    if methods is None:
        methods = ["GET"]

    def decorator(func: Callable):
        # Register endpoint with the API router
        # Implementation depends on specific framework integration
        return func

    return decorator


def require_auth(permission: PermissionLevel = PermissionLevel.READ):
    """Decorator for requiring authentication."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Implement authentication check
            # For now, just pass through
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit(requests_per_minute: int = 60):
    """Decorator for rate limiting."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Implement rate limiting
            # For now, just pass through
            return await func(*args, **kwargs)

        return wrapper

    return decorator
