"""
Advanced Workflow Orchestration Engine for Agno Framework Integration
Implements multiple execution strategies, conditional logic, and performance optimization.
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from .exceptions import AgnoFrameworkError
from .types import ExecutionMode, ExecutionResult

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """Workflow execution strategies"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"  # Automatically chooses best strategy


class ErrorHandlingStrategy(Enum):
    """Error handling strategies for workflow components"""

    FAIL_FAST = "fail_fast"
    CONTINUE = "continue"
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"


class WorkflowStatus(Enum):
    """Workflow execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ComponentNode:
    """Individual component in a workflow"""

    id: str
    component_name: str
    configuration: dict[str, Any]
    inputs: dict[str, Any]
    dependencies: list[str] = field(default_factory=list)
    error_strategy: ErrorHandlingStrategy = ErrorHandlingStrategy.RETRY
    retry_count: int = 3
    timeout: float | None = None
    condition: str | None = None  # JavaScript-like condition expression
    priority: int = 1  # For execution ordering
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ComponentConnection:
    """Connection between workflow components"""

    from_component: str
    to_component: str
    output_key: str
    input_key: str
    transformation: str | None = None  # JavaScript-like transformation expression
    condition: str | None = None  # Conditional connection
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    components: list[ComponentNode] = field(default_factory=list)
    connections: list[ComponentConnection] = field(default_factory=list)
    execution_strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    error_handling: ErrorHandlingStrategy = ErrorHandlingStrategy.RETRY
    timeout_config: dict[str, float] = field(default_factory=lambda: {"default": 300.0})
    global_variables: dict[str, Any] = field(default_factory=dict)
    triggers: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()


@dataclass
class WorkflowExecution:
    """Workflow execution state and tracking"""

    workflow_id: str
    execution_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: float | None = None
    component_results: dict[str, ExecutionResult] = field(default_factory=dict)
    component_status: dict[str, str] = field(default_factory=dict)
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    progress: float = 0.0
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())


@dataclass
class ValidationResult:
    """Workflow validation result"""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    performance_hints: list[str] = field(default_factory=list)


class ConditionalEvaluator:
    """Safe evaluation of conditional expressions"""

    @staticmethod
    def evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
        """Safely evaluate a condition expression"""
        if not condition:
            return True

        try:
            # Simple expression evaluation (can be extended with a proper parser)
            # For now, support basic comparisons and logical operators

            # Replace context variables
            expression = condition
            for key, value in context.items():
                if isinstance(value, str):
                    expression = expression.replace(f"${key}", f"'{value}'")
                else:
                    expression = expression.replace(f"${key}", str(value))

            # Basic safety check - only allow safe operations
            allowed_chars = set(
                "()[]{}.,;:+-*/<>=!&|01234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ \t\n'\""
            )
            if not all(c in allowed_chars for c in expression):
                logger.warning(f"Unsafe characters in condition: {condition}")
                return False

            # Evaluate expression (in production, use a proper expression parser)
            result = eval(expression, {"__builtins__": {}}, {})
            return bool(result)

        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False

    @staticmethod
    def transform_data(transformation: str, data: Any, context: dict[str, Any]) -> Any:
        """Apply data transformation"""
        if not transformation:
            return data

        try:
            # Simple transformation support
            # In production, use a proper expression parser/transformer
            result = data

            # Example transformations:
            if transformation == "upper":
                result = str(data).upper()
            elif transformation == "lower":
                result = str(data).lower()
            elif transformation.startswith("$."):
                # JSONPath-like extraction
                path = transformation[2:]
                if isinstance(data, dict):
                    result = data.get(path, data)

            return result

        except Exception as e:
            logger.error(f"Error applying transformation '{transformation}': {e}")
            return data


class AgnoWorkflowEngine:
    """Advanced workflow orchestration engine for Agno framework"""

    def __init__(self, framework_manager):
        self.framework_manager = framework_manager
        self.workflow_registry: dict[str, WorkflowDefinition] = {}
        self.active_executions: dict[str, WorkflowExecution] = {}
        self.execution_history: list[WorkflowExecution] = []
        self.conditional_evaluator = ConditionalEvaluator()
        self.execution_queue = asyncio.Queue()
        self.max_concurrent_workflows = 10
        self.max_history_size = 1000

        # Performance optimization settings
        self.enable_caching = True
        self.component_cache: dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info("AgnoWorkflowEngine initialized")

    async def register_workflow(self, workflow: WorkflowDefinition) -> str:
        """Register a workflow definition"""
        try:
            # Validate workflow
            validation = self.validate_workflow(workflow)
            if not validation.is_valid:
                raise AgnoFrameworkError(f"Invalid workflow: {', '.join(validation.errors)}")

            # Store workflow
            self.workflow_registry[workflow.id] = workflow

            logger.info(f"Registered workflow: {workflow.name} ({workflow.id})")
            return workflow.id

        except Exception as e:
            logger.error(f"Failed to register workflow {workflow.name}: {e}")
            raise AgnoFrameworkError(f"Workflow registration failed: {e}")

    async def execute_workflow(
        self, workflow_id: str, initial_inputs: dict[str, Any], execution_config: dict[str, Any] | None = None
    ) -> str:
        """Execute a registered workflow"""
        if workflow_id not in self.workflow_registry:
            raise AgnoFrameworkError(f"Workflow not found: {workflow_id}")

        workflow = self.workflow_registry[workflow_id]
        execution_config = execution_config or {}

        # Create execution context
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            execution_id=str(uuid.uuid4()),
            status=WorkflowStatus.PENDING,
            context=initial_inputs.copy(),
            metadata={"initial_inputs": initial_inputs, "config": execution_config, "workflow_name": workflow.name},
        )

        # Add to active executions
        self.active_executions[execution.execution_id] = execution

        # Queue for execution
        await self.execution_queue.put(execution)

        # Start execution in background
        asyncio.create_task(self._execute_workflow_async(execution))

        logger.info(f"Queued workflow execution: {workflow.name} ({execution.execution_id})")
        return execution.execution_id

    async def _execute_workflow_async(self, execution: WorkflowExecution):
        """Execute workflow asynchronously"""
        workflow = self.workflow_registry[execution.workflow_id]

        try:
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now()

            logger.info(f"Starting workflow execution: {workflow.name} ({execution.execution_id})")

            # Execute based on strategy
            if workflow.execution_strategy == ExecutionStrategy.SEQUENTIAL:
                await self._execute_sequential(workflow, execution)
            elif workflow.execution_strategy == ExecutionStrategy.PARALLEL:
                await self._execute_parallel(workflow, execution)
            elif workflow.execution_strategy == ExecutionStrategy.CONDITIONAL:
                await self._execute_conditional(workflow, execution)
            elif workflow.execution_strategy == ExecutionStrategy.PIPELINE:
                await self._execute_pipeline(workflow, execution)
            elif workflow.execution_strategy == ExecutionStrategy.ADAPTIVE:
                await self._execute_adaptive(workflow, execution)
            else:
                raise AgnoFrameworkError(f"Unsupported execution strategy: {workflow.execution_strategy}")

            execution.status = WorkflowStatus.COMPLETED
            execution.progress = 100.0

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.errors.append(
                {"type": "workflow_execution_error", "message": str(e), "timestamp": datetime.now().isoformat()}
            )
            logger.error(f"Workflow execution failed: {workflow.name} ({execution.execution_id}): {e}")

        finally:
            execution.end_time = datetime.now()
            if execution.start_time:
                execution.duration = (execution.end_time - execution.start_time).total_seconds()

            # Move to history
            self._move_to_history(execution)

    async def _execute_sequential(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """Execute components sequentially"""
        # Sort components by dependencies
        sorted_components = self._topological_sort(workflow.components)
        total_components = len(sorted_components)

        for i, component in enumerate(sorted_components):
            try:
                # Check if execution is cancelled
                if execution.status == WorkflowStatus.CANCELLED:
                    break

                # Evaluate component condition
                if not self.conditional_evaluator.evaluate_condition(component.condition, execution.context):
                    logger.info(f"Skipping component {component.id} due to condition")
                    execution.component_status[component.id] = "skipped"
                    continue

                # Execute component
                result = await self._execute_component(component, execution)
                execution.component_results[component.id] = result
                execution.component_status[component.id] = "completed"

                # Update progress
                execution.progress = ((i + 1) / total_components) * 100

                # Update context with component output
                if result.success and result.output:
                    execution.context.update({f"{component.id}_output": result.output})

            except Exception as e:
                await self._handle_component_error(component, e, execution)

    async def _execute_parallel(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """Execute independent components in parallel"""
        # Group components by dependency level
        dependency_levels = self._group_by_dependency_level(workflow.components)

        for level_components in dependency_levels:
            # Execute all components in this level concurrently
            tasks = []
            for component in level_components:
                if self.conditional_evaluator.evaluate_condition(component.condition, execution.context):
                    task = asyncio.create_task(self._execute_component(component, execution))
                    tasks.append((component, task))
                else:
                    execution.component_status[component.id] = "skipped"

            # Wait for all tasks in this level to complete
            for component, task in tasks:
                try:
                    result = await task
                    execution.component_results[component.id] = result
                    execution.component_status[component.id] = "completed"

                    if result.success and result.output:
                        execution.context.update({f"{component.id}_output": result.output})

                except Exception as e:
                    await self._handle_component_error(component, e, execution)

    async def _execute_conditional(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """Execute components based on dynamic conditions"""
        remaining_components = workflow.components.copy()
        executed_components = set()

        while remaining_components:
            executed_in_round = False

            for component in remaining_components.copy():
                # Check if dependencies are satisfied
                if all(dep in executed_components for dep in component.dependencies):
                    # Check condition
                    if self.conditional_evaluator.evaluate_condition(component.condition, execution.context):
                        try:
                            result = await self._execute_component(component, execution)
                            execution.component_results[component.id] = result
                            execution.component_status[component.id] = "completed"

                            if result.success and result.output:
                                execution.context.update({f"{component.id}_output": result.output})

                            executed_components.add(component.id)
                            remaining_components.remove(component)
                            executed_in_round = True

                        except Exception as e:
                            await self._handle_component_error(component, e, execution)
                            executed_components.add(component.id)  # Mark as processed
                            remaining_components.remove(component)
                    else:
                        # Condition not met, skip
                        execution.component_status[component.id] = "skipped"
                        executed_components.add(component.id)
                        remaining_components.remove(component)
                        executed_in_round = True

            if not executed_in_round:
                # Circular dependency or unsatisfied conditions
                remaining_ids = [c.id for c in remaining_components]
                raise AgnoFrameworkError(f"Cannot execute remaining components: {remaining_ids}")

    async def _execute_pipeline(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """Execute components in a data pipeline fashion"""
        # Build data flow graph
        flow_graph = self._build_data_flow_graph(workflow)

        # Start with initial data
        data_streams = {"initial": execution.context}

        for stage in flow_graph:
            stage_results = {}

            # Process all components in this stage
            for component in stage:
                try:
                    # Prepare inputs from data streams
                    component_inputs = self._prepare_pipeline_inputs(component, data_streams, workflow.connections)

                    # Execute component
                    component.inputs.update(component_inputs)
                    result = await self._execute_component(component, execution)

                    execution.component_results[component.id] = result
                    execution.component_status[component.id] = "completed"

                    if result.success:
                        stage_results[component.id] = result.output

                except Exception as e:
                    await self._handle_component_error(component, e, execution)

            # Update data streams for next stage
            data_streams.update(stage_results)

    async def _execute_adaptive(self, workflow: WorkflowDefinition, execution: WorkflowExecution):
        """Automatically choose best execution strategy"""
        # Analyze workflow characteristics
        component_count = len(workflow.components)
        dependency_complexity = self._calculate_dependency_complexity(workflow.components)
        has_conditions = any(c.condition for c in workflow.components)

        # Choose strategy based on analysis
        if has_conditions:
            chosen_strategy = ExecutionStrategy.CONDITIONAL
        elif dependency_complexity > 0.7 and component_count > 10:
            chosen_strategy = ExecutionStrategy.PIPELINE
        elif dependency_complexity < 0.3:
            chosen_strategy = ExecutionStrategy.PARALLEL
        else:
            chosen_strategy = ExecutionStrategy.SEQUENTIAL

        logger.info(f"Adaptive execution chose strategy: {chosen_strategy}")

        # Execute with chosen strategy
        original_strategy = workflow.execution_strategy
        workflow.execution_strategy = chosen_strategy

        try:
            if chosen_strategy == ExecutionStrategy.SEQUENTIAL:
                await self._execute_sequential(workflow, execution)
            elif chosen_strategy == ExecutionStrategy.PARALLEL:
                await self._execute_parallel(workflow, execution)
            elif chosen_strategy == ExecutionStrategy.CONDITIONAL:
                await self._execute_conditional(workflow, execution)
            elif chosen_strategy == ExecutionStrategy.PIPELINE:
                await self._execute_pipeline(workflow, execution)
        finally:
            workflow.execution_strategy = original_strategy

    async def _execute_component(self, component: ComponentNode, execution: WorkflowExecution) -> ExecutionResult:
        """Execute a single component"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(component)
            if self.enable_caching and cache_key in self.component_cache:
                cached_result, cache_time = self.component_cache[cache_key]
                if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                    logger.debug(f"Using cached result for component {component.id}")
                    return cached_result

            # Execute component through framework manager
            start_time = datetime.now()
            result = await self.framework_manager.execute_component(
                component.component_name, component.inputs, component.configuration
            )

            # Cache successful results
            if self.enable_caching and result.success:
                self.component_cache[cache_key] = (result, datetime.now())

            execution_time = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Component {component.id} executed in {execution_time:.3f}s")

            return result

        except Exception as e:
            logger.error(f"Component execution failed: {component.id}: {e}")
            return ExecutionResult(
                success=False,
                output={},
                error=str(e),
                execution_time=0.0,
                mode=ExecutionMode.FAILED,
                metadata={"component_id": component.id, "error_type": type(e).__name__},
            )

    async def _handle_component_error(self, component: ComponentNode, error: Exception, execution: WorkflowExecution):
        """Handle component execution errors"""
        error_info = {
            "component_id": component.id,
            "component_name": component.component_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "strategy": component.error_strategy.value,
        }

        execution.errors.append(error_info)
        execution.component_status[component.id] = "failed"

        # Handle based on error strategy
        if component.error_strategy == ErrorHandlingStrategy.FAIL_FAST:
            raise AgnoFrameworkError(f"Component {component.id} failed: {error}")

        elif component.error_strategy == ErrorHandlingStrategy.RETRY:
            # Implement retry logic
            for attempt in range(component.retry_count):
                try:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    result = await self._execute_component(component, execution)
                    execution.component_results[component.id] = result
                    execution.component_status[component.id] = "completed"
                    return
                except Exception as retry_error:
                    if attempt == component.retry_count - 1:
                        logger.error(f"All retry attempts failed for {component.id}")
                        break

        elif component.error_strategy == ErrorHandlingStrategy.FALLBACK:
            # Execute fallback component if specified
            fallback_name = component.metadata.get("fallback_component")
            if fallback_name:
                try:
                    fallback_result = await self.framework_manager.execute_component(
                        fallback_name, component.inputs, component.configuration
                    )
                    execution.component_results[component.id] = fallback_result
                    execution.component_status[component.id] = "fallback_completed"
                except Exception:
                    logger.error(f"Fallback also failed for {component.id}")

        # Continue execution for other strategies
        logger.warning(f"Component {component.id} failed, continuing with strategy: {component.error_strategy}")

    def validate_workflow(self, workflow: WorkflowDefinition) -> ValidationResult:
        """Validate workflow definition"""
        errors = []
        warnings = []
        suggestions = []
        performance_hints = []

        # Check for circular dependencies
        if self._has_circular_dependencies(workflow.components):
            errors.append("Workflow contains circular dependencies")

        # Validate component connections
        component_ids = {c.id for c in workflow.components}
        for connection in workflow.connections:
            if connection.from_component not in component_ids:
                errors.append(f"Connection references unknown component: {connection.from_component}")
            if connection.to_component not in component_ids:
                errors.append(f"Connection references unknown component: {connection.to_component}")

        # Check component configurations
        for component in workflow.components:
            component_info = self.framework_manager.get_component_info(component.component_name)
            if not component_info:
                errors.append(f"Unknown component: {component.component_name}")

            # Check for missing required inputs
            if hasattr(component_info, "required_inputs"):
                missing_inputs = set(component_info.required_inputs) - set(component.inputs.keys())
                if missing_inputs:
                    warnings.append(f"Component {component.id} missing inputs: {missing_inputs}")

        # Performance suggestions
        if len(workflow.components) > 20:
            performance_hints.append("Consider breaking large workflows into smaller sub-workflows")

        if workflow.execution_strategy == ExecutionStrategy.SEQUENTIAL and len(workflow.components) > 10:
            performance_hints.append("Consider using parallel execution strategy for better performance")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            performance_hints=performance_hints,
        )

    def optimize_workflow_execution(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        """Optimize workflow for better performance"""
        optimized = WorkflowDefinition(**workflow.__dict__)

        # Reorder components for better parallelization
        optimized.components = self._optimize_component_order(workflow.components)

        # Add caching hints for expensive components
        for component in optimized.components:
            if component.metadata.get("expensive_operation"):
                component.metadata["cache_enabled"] = True

        # Optimize execution strategy
        if self._should_use_parallel_execution(workflow):
            optimized.execution_strategy = ExecutionStrategy.PARALLEL

        return optimized

    def get_execution_status(self, execution_id: str) -> dict[str, Any] | None:
        """Get current execution status"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            # Check history
            for hist_exec in self.execution_history:
                if hist_exec.execution_id == execution_id:
                    execution = hist_exec
                    break

        if not execution:
            return None

        workflow = self.workflow_registry.get(execution.workflow_id)
        total_components = len(workflow.components) if workflow else 0

        return {
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "workflow_name": workflow.name if workflow else "Unknown",
            "status": execution.status.value,
            "start_time": execution.start_time.isoformat() if execution.start_time else None,
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "duration": execution.duration,
            "progress": execution.progress,
            "completed_components": len([s for s in execution.component_status.values() if s == "completed"]),
            "total_components": total_components,
            "failed_components": len([s for s in execution.component_status.values() if s == "failed"]),
            "component_status": execution.component_status,
            "errors": execution.errors,
            "warnings": execution.warnings,
        }

    def get_workflow_analytics(self, workflow_id: str) -> dict[str, Any]:
        """Get analytics for a specific workflow"""
        if workflow_id not in self.workflow_registry:
            return {}

        workflow = self.workflow_registry[workflow_id]

        # Get execution history for this workflow
        executions = [e for e in self.execution_history if e.workflow_id == workflow_id]

        if not executions:
            return {"workflow_id": workflow_id, "no_executions": True}

        # Calculate analytics
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.status == WorkflowStatus.COMPLETED])
        failed_executions = len([e for e in executions if e.status == WorkflowStatus.FAILED])

        durations = [e.duration for e in executions if e.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow.name,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
            "average_duration": avg_duration,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "last_execution": max([e.start_time for e in executions if e.start_time]).isoformat()
            if executions
            else None,
        }

    # Helper methods

    def _topological_sort(self, components: list[ComponentNode]) -> list[ComponentNode]:
        """Sort components by dependencies using topological sort"""
        visited = set()
        temp_visited = set()
        result = []

        def visit(component):
            if component.id in temp_visited:
                raise AgnoFrameworkError("Circular dependency detected")
            if component.id in visited:
                return

            temp_visited.add(component.id)

            # Visit dependencies first
            for dep_id in component.dependencies:
                dep_component = next((c for c in components if c.id == dep_id), None)
                if dep_component:
                    visit(dep_component)

            temp_visited.remove(component.id)
            visited.add(component.id)
            result.append(component)

        for component in components:
            if component.id not in visited:
                visit(component)

        return result

    def _group_by_dependency_level(self, components: list[ComponentNode]) -> list[list[ComponentNode]]:
        """Group components by dependency level for parallel execution"""
        levels = []
        remaining = components.copy()
        processed = set()

        while remaining:
            current_level = []

            for component in remaining.copy():
                # Check if all dependencies are processed
                if all(dep in processed for dep in component.dependencies):
                    current_level.append(component)
                    remaining.remove(component)
                    processed.add(component.id)

            if not current_level:
                # Circular dependency or error
                raise AgnoFrameworkError("Cannot resolve component dependencies")

            levels.append(current_level)

        return levels

    def _build_data_flow_graph(self, workflow: WorkflowDefinition) -> list[list[ComponentNode]]:
        """Build data flow graph for pipeline execution"""
        # Similar to dependency grouping but considering data flow
        return self._group_by_dependency_level(workflow.components)

    def _prepare_pipeline_inputs(
        self, component: ComponentNode, data_streams: dict[str, Any], connections: list[ComponentConnection]
    ) -> dict[str, Any]:
        """Prepare inputs for pipeline component from data streams"""
        inputs = {}

        # Find connections targeting this component
        for connection in connections:
            if connection.to_component == component.id:
                source_data = data_streams.get(connection.from_component, {})

                if isinstance(source_data, dict) and connection.output_key in source_data:
                    value = source_data[connection.output_key]

                    # Apply transformation if specified
                    if connection.transformation:
                        value = self.conditional_evaluator.transform_data(
                            connection.transformation, value, data_streams
                        )

                    inputs[connection.input_key] = value

        return inputs

    def _calculate_dependency_complexity(self, components: list[ComponentNode]) -> float:
        """Calculate dependency complexity score (0-1)"""
        if not components:
            return 0.0

        total_dependencies = sum(len(c.dependencies) for c in components)
        max_possible = len(components) * (len(components) - 1)

        return total_dependencies / max_possible if max_possible > 0 else 0.0

    def _has_circular_dependencies(self, components: list[ComponentNode]) -> bool:
        """Check for circular dependencies"""
        try:
            self._topological_sort(components)
            return False
        except AgnoFrameworkError:
            return True

    def _generate_cache_key(self, component: ComponentNode) -> str:
        """Generate cache key for component"""
        import hashlib

        # Create hash from component name, inputs, and configuration
        data = {"name": component.component_name, "inputs": component.inputs, "config": component.configuration}

        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _should_use_parallel_execution(self, workflow: WorkflowDefinition) -> bool:
        """Determine if workflow should use parallel execution"""
        dependency_complexity = self._calculate_dependency_complexity(workflow.components)
        return dependency_complexity < 0.3 and len(workflow.components) > 3

    def _optimize_component_order(self, components: list[ComponentNode]) -> list[ComponentNode]:
        """Optimize component execution order"""
        # Sort by priority first, then by dependencies
        return sorted(components, key=lambda c: (c.priority, len(c.dependencies)))

    def _move_to_history(self, execution: WorkflowExecution):
        """Move execution to history and cleanup"""
        if execution.execution_id in self.active_executions:
            del self.active_executions[execution.execution_id]

        self.execution_history.append(execution)

        # Limit history size
        if len(self.execution_history) > self.max_history_size:
            self.execution_history = self.execution_history[-self.max_history_size :]

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.end_time = datetime.now()
            logger.info(f"Cancelled workflow execution: {execution_id}")
            return True
        return False

    async def pause_execution(self, execution_id: str) -> bool:
        """Pause a running workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.PAUSED
            logger.info(f"Paused workflow execution: {execution_id}")
            return True
        return False

    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused workflow execution"""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            if execution.status == WorkflowStatus.PAUSED:
                execution.status = WorkflowStatus.RUNNING
                logger.info(f"Resumed workflow execution: {execution_id}")
                return True
        return False

    def get_workflow_templates(self) -> list[dict[str, Any]]:
        """Get available workflow templates"""
        templates = [
            {
                "id": "simple_sequential",
                "name": "Simple Sequential Workflow",
                "description": "Basic sequential execution template",
                "execution_strategy": "sequential",
                "component_count": 3,
            },
            {
                "id": "parallel_processing",
                "name": "Parallel Processing Workflow",
                "description": "Parallel execution for independent tasks",
                "execution_strategy": "parallel",
                "component_count": 5,
            },
            {
                "id": "conditional_flow",
                "name": "Conditional Workflow",
                "description": "Dynamic execution based on conditions",
                "execution_strategy": "conditional",
                "component_count": 4,
            },
        ]
        return templates

    def create_workflow_from_template(self, template_id: str, name: str, description: str) -> WorkflowDefinition:
        """Create a new workflow from a template"""
        # This would typically load predefined templates
        # For now, return a basic template
        return WorkflowDefinition(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            version="1.0.0",
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
        )
