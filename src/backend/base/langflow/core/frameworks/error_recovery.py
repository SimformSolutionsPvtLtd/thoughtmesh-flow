"""
Advanced Error Recovery System for Agno Framework Integration.

This module provides comprehensive error recovery, circuit breaker patterns,
retry mechanisms, and fault tolerance for the Langflow-Agno integration.
"""

import asyncio
import json
import logging
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Union

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for recovery prioritization."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RecoveryStrategy(Enum):
    """Available recovery strategies."""

    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    RESTART_COMPONENT = "restart_component"
    ESCALATE = "escalate"


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ErrorContext:
    """Context information for error tracking and recovery."""

    error_id: str
    timestamp: datetime
    component: str
    operation: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    stack_trace: str
    metadata: dict[str, Any] = field(default_factory=dict)
    recovery_attempts: int = 0
    max_retries: int = 3
    last_recovery_time: datetime | None = None


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""

    failure_threshold: int = 5
    timeout_duration: int = 60  # seconds
    success_threshold: int = 3
    monitoring_window: int = 300  # seconds


class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None
        self.failures: list[datetime] = []

    def _clean_old_failures(self):
        """Remove failures outside monitoring window."""
        cutoff = datetime.now() - timedelta(seconds=self.config.monitoring_window)
        self.failures = [f for f in self.failures if f > cutoff]

    def can_execute(self) -> bool:
        """Check if execution is allowed based on circuit state."""
        self._clean_old_failures()

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_time and datetime.now() - self.last_failure_time > timedelta(
                seconds=self.config.timeout_duration
            ):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
            return False

        if self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def record_success(self):
        """Record successful execution."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.failures.clear()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def record_failure(self):
        """Record failed execution."""
        self.last_failure_time = datetime.now()
        self.failures.append(self.last_failure_time)
        self._clean_old_failures()

        if self.state == CircuitState.CLOSED:
            if len(self.failures) >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.success_count = 0


class ErrorRecoverySystem:
    """Advanced error recovery system with multiple strategies."""

    def __init__(self):
        self.error_history: dict[str, list[ErrorContext]] = {}
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.recovery_strategies: dict[str, list[RecoveryStrategy]] = {}
        self.fallback_handlers: dict[str, Callable] = {}
        self.error_patterns: dict[str, dict[str, Any]] = {}
        self.metrics = {
            "total_errors": 0,
            "recovered_errors": 0,
            "failed_recoveries": 0,
            "circuit_breaker_activations": 0,
        }

    def register_component(
        self,
        component_name: str,
        strategies: list[RecoveryStrategy],
        circuit_config: CircuitBreakerConfig | None = None,
        fallback_handler: Callable | None = None,
    ):
        """Register a component with recovery strategies."""
        self.recovery_strategies[component_name] = strategies

        if circuit_config:
            self.circuit_breakers[component_name] = CircuitBreaker(circuit_config)

        if fallback_handler:
            self.fallback_handlers[component_name] = fallback_handler

        logger.info(f"Registered recovery strategies for {component_name}: {strategies}")

    def _generate_error_id(self, component: str, operation: str) -> str:
        """Generate unique error ID."""
        timestamp = int(time.time() * 1000)
        return f"{component}_{operation}_{timestamp}"

    def _determine_severity(self, error: Exception, component: str) -> ErrorSeverity:
        """Determine error severity based on type and component."""
        error_type = type(error).__name__

        # Critical errors
        if error_type in ["SystemExit", "KeyboardInterrupt", "MemoryError"]:
            return ErrorSeverity.CRITICAL

        # High severity errors
        if error_type in ["ConnectionError", "TimeoutError", "PermissionError"]:
            return ErrorSeverity.HIGH

        # Medium severity errors
        if error_type in ["ValueError", "TypeError", "AttributeError"]:
            return ErrorSeverity.MEDIUM

        # Default to low severity
        return ErrorSeverity.LOW

    def record_error(
        self, error: Exception, component: str, operation: str, metadata: dict[str, Any] | None = None
    ) -> ErrorContext:
        """Record an error with context information."""
        error_id = self._generate_error_id(component, operation)
        severity = self._determine_severity(error, component)

        error_context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            component=component,
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            severity=severity,
            stack_trace=traceback.format_exc(),
            metadata=metadata or {},
        )

        # Store in history
        if component not in self.error_history:
            self.error_history[component] = []
        self.error_history[component].append(error_context)

        # Update metrics
        self.metrics["total_errors"] += 1

        # Record circuit breaker failure if applicable
        if component in self.circuit_breakers:
            self.circuit_breakers[component].record_failure()

        logger.error(f"Error recorded: {error_id} - {error_context.error_message}")
        return error_context

    async def attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Attempt to recover from an error using configured strategies."""
        component = error_context.component
        strategies = self.recovery_strategies.get(component, [RecoveryStrategy.RETRY])

        logger.info(f"Attempting recovery for {error_context.error_id} using strategies: {strategies}")

        for strategy in strategies:
            try:
                if await self._execute_recovery_strategy(strategy, error_context):
                    self.metrics["recovered_errors"] += 1
                    error_context.last_recovery_time = datetime.now()
                    logger.info(f"Successfully recovered from {error_context.error_id} using {strategy}")
                    return True
            except Exception as e:
                logger.warning(f"Recovery strategy {strategy} failed for {error_context.error_id}: {e}")
                continue

        self.metrics["failed_recoveries"] += 1
        logger.error(f"All recovery strategies failed for {error_context.error_id}")
        return False

    async def _execute_recovery_strategy(self, strategy: RecoveryStrategy, error_context: ErrorContext) -> bool:
        """Execute a specific recovery strategy."""
        if strategy == RecoveryStrategy.RETRY:
            return await self._retry_strategy(error_context)

        if strategy == RecoveryStrategy.FALLBACK:
            return await self._fallback_strategy(error_context)

        if strategy == RecoveryStrategy.CIRCUIT_BREAKER:
            return await self._circuit_breaker_strategy(error_context)

        if strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
            return await self._graceful_degradation_strategy(error_context)

        if strategy == RecoveryStrategy.RESTART_COMPONENT:
            return await self._restart_component_strategy(error_context)

        if strategy == RecoveryStrategy.ESCALATE:
            return await self._escalate_strategy(error_context)

        return False

    async def _retry_strategy(self, error_context: ErrorContext) -> bool:
        """Implement retry strategy with exponential backoff."""
        if error_context.recovery_attempts >= error_context.max_retries:
            logger.warning(f"Max retries exceeded for {error_context.error_id}")
            return False

        error_context.recovery_attempts += 1

        # Exponential backoff
        delay = min(2**error_context.recovery_attempts, 60)
        await asyncio.sleep(delay)

        logger.info(f"Retry attempt {error_context.recovery_attempts} for {error_context.error_id}")
        return True

    async def _fallback_strategy(self, error_context: ErrorContext) -> bool:
        """Implement fallback strategy using registered handlers."""
        component = error_context.component

        if component not in self.fallback_handlers:
            logger.warning(f"No fallback handler registered for {component}")
            return False

        try:
            fallback_handler = self.fallback_handlers[component]
            result = await fallback_handler(error_context)
            logger.info(f"Fallback handler executed successfully for {error_context.error_id}")
            return bool(result)
        except Exception as e:
            logger.error(f"Fallback handler failed for {error_context.error_id}: {e}")
            return False

    async def _circuit_breaker_strategy(self, error_context: ErrorContext) -> bool:
        """Implement circuit breaker strategy."""
        component = error_context.component

        if component not in self.circuit_breakers:
            logger.warning(f"No circuit breaker configured for {component}")
            return False

        circuit_breaker = self.circuit_breakers[component]

        if not circuit_breaker.can_execute():
            logger.warning(f"Circuit breaker is open for {component}")
            self.metrics["circuit_breaker_activations"] += 1
            return False

        # Circuit breaker allows execution
        return True

    async def _graceful_degradation_strategy(self, error_context: ErrorContext) -> bool:
        """Implement graceful degradation strategy."""
        # Reduce functionality while maintaining core operations
        logger.info(f"Applying graceful degradation for {error_context.component}")

        # This could involve:
        # - Disabling non-essential features
        # - Using cached data
        # - Reducing quality/precision
        # - Switching to simpler algorithms

        return True

    async def _restart_component_strategy(self, error_context: ErrorContext) -> bool:
        """Implement component restart strategy."""
        component = error_context.component
        logger.info(f"Attempting to restart component: {component}")

        # This would involve restarting the specific component
        # Implementation depends on the component architecture

        return True

    async def _escalate_strategy(self, error_context: ErrorContext) -> bool:
        """Implement error escalation strategy."""
        logger.critical(f"Escalating error {error_context.error_id} to higher level handling")

        # This could involve:
        # - Notifying administrators
        # - Creating support tickets
        # - Triggering emergency procedures
        # - Shutting down affected systems

        return False  # Escalation doesn't "recover" the error

    def with_recovery(self, component: str, operation: str, metadata: dict[str, Any] | None = None):
        """Decorator for automatic error recovery."""

        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    # Check circuit breaker if configured
                    if component in self.circuit_breakers:
                        circuit_breaker = self.circuit_breakers[component]
                        if not circuit_breaker.can_execute():
                            raise Exception(f"Circuit breaker is open for {component}")

                    result = await func(*args, **kwargs)

                    # Record success for circuit breaker
                    if component in self.circuit_breakers:
                        self.circuit_breakers[component].record_success()

                    return result

                except Exception as e:
                    error_context = self.record_error(e, component, operation, metadata)

                    # Attempt recovery
                    if await self.attempt_recovery(error_context):
                        # Retry the operation after successful recovery
                        try:
                            return await func(*args, **kwargs)
                        except Exception as retry_error:
                            logger.error(f"Operation failed after recovery: {retry_error}")
                            raise
                    else:
                        raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    # Check circuit breaker if configured
                    if component in self.circuit_breakers:
                        circuit_breaker = self.circuit_breakers[component]
                        if not circuit_breaker.can_execute():
                            raise Exception(f"Circuit breaker is open for {component}")

                    result = func(*args, **kwargs)

                    # Record success for circuit breaker
                    if component in self.circuit_breakers:
                        self.circuit_breakers[component].record_success()

                    return result

                except Exception as e:
                    error_context = self.record_error(e, component, operation, metadata)

                    # For sync functions, we can't await recovery
                    # Log the error and re-raise
                    logger.error(f"Error in sync function {operation}: {e}")
                    raise

            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    def get_error_statistics(self, component: str | None = None) -> dict[str, Any]:
        """Get error statistics for monitoring."""
        stats = {"global_metrics": self.metrics.copy(), "component_stats": {}}

        components = [component] if component else self.error_history.keys()

        for comp in components:
            if comp not in self.error_history:
                continue

            errors = self.error_history[comp]
            comp_stats = {
                "total_errors": len(errors),
                "errors_by_severity": {},
                "recent_errors": len([e for e in errors if datetime.now() - e.timestamp < timedelta(hours=1)]),
                "error_types": {},
            }

            for error in errors:
                # Count by severity
                severity = error.severity.value
                comp_stats["errors_by_severity"][severity] = comp_stats["errors_by_severity"].get(severity, 0) + 1

                # Count by type
                error_type = error.error_type
                comp_stats["error_types"][error_type] = comp_stats["error_types"].get(error_type, 0) + 1

            # Circuit breaker status
            if comp in self.circuit_breakers:
                circuit_breaker = self.circuit_breakers[comp]
                comp_stats["circuit_breaker"] = {
                    "state": circuit_breaker.state.value,
                    "failure_count": len(circuit_breaker.failures),
                    "can_execute": circuit_breaker.can_execute(),
                }

            stats["component_stats"][comp] = comp_stats

        return stats

    def export_error_report(self, component: str | None = None) -> str:
        """Export detailed error report."""
        stats = self.get_error_statistics(component)

        report = {"timestamp": datetime.now().isoformat(), "statistics": stats, "detailed_errors": {}}

        components = [component] if component else self.error_history.keys()

        for comp in components:
            if comp not in self.error_history:
                continue

            report["detailed_errors"][comp] = [
                {
                    "error_id": error.error_id,
                    "timestamp": error.timestamp.isoformat(),
                    "operation": error.operation,
                    "error_type": error.error_type,
                    "error_message": error.error_message,
                    "severity": error.severity.value,
                    "recovery_attempts": error.recovery_attempts,
                    "metadata": error.metadata,
                }
                for error in self.error_history[comp][-50:]  # Last 50 errors
            ]

        return json.dumps(report, indent=2)


# Global error recovery system instance
error_recovery_system = ErrorRecoverySystem()


# Convenience functions
def register_component_recovery(
    component_name: str,
    strategies: list[RecoveryStrategy],
    circuit_config: CircuitBreakerConfig | None = None,
    fallback_handler: Callable | None = None,
):
    """Register recovery strategies for a component."""
    return error_recovery_system.register_component(component_name, strategies, circuit_config, fallback_handler)


def with_recovery(component: str, operation: str, metadata: dict[str, Any] | None = None):
    """Decorator for automatic error recovery."""
    return error_recovery_system.with_recovery(component, operation, metadata)


async def recover_from_error(error_context: ErrorContext) -> bool:
    """Attempt to recover from a specific error."""
    return await error_recovery_system.attempt_recovery(error_context)


def get_recovery_statistics(component: str | None = None) -> dict[str, Any]:
    """Get error recovery statistics."""
    return error_recovery_system.get_error_statistics(component)
