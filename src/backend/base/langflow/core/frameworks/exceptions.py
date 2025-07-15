"""Framework exceptions for the Langflow framework abstraction layer."""


class FrameworkError(Exception):
    """Base exception for framework-related errors."""


class FrameworkNotInitializedError(FrameworkError):
    """Raised when trying to use an uninitialized framework."""


class FrameworkInitializationError(FrameworkError):
    """Raised when framework initialization fails."""


class ComponentNotFoundError(FrameworkError):
    """Raised when a component is not found."""


class ComponentDiscoveryError(FrameworkError):
    """Raised when component discovery fails."""


class ComponentExecutionError(FrameworkError):
    """Raised when component execution fails."""


class ConfigurationValidationError(FrameworkError):
    """Raised when configuration validation fails."""


class FlowExecutionError(FrameworkError):
    """Raised when flow execution fails."""
