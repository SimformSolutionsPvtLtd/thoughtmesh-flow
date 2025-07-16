"""
Extensible Plugin System for Agno Framework Integration.

This module provides a comprehensive plugin architecture that allows
dynamic loading, registration, and management of framework extensions.
"""

import asyncio
import importlib
import inspect
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Type

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported by the system."""

    COMPONENT = "component"
    PROCESSOR = "processor"
    VALIDATOR = "validator"
    CONNECTOR = "connector"
    MIDDLEWARE = "middleware"
    EXTENSION = "extension"


class PluginStatus(Enum):
    """Plugin lifecycle status."""

    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADED = "unloaded"


@dataclass
class PluginMetadata:
    """Metadata for plugin registration and management."""

    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    entry_point: str = ""
    module_path: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    status: PluginStatus = PluginStatus.DISCOVERED


class PluginError(Exception):
    """Custom exception for plugin-related errors."""

    def __init__(self, message: str, plugin_name: str | None = None):
        self.plugin_name = plugin_name
        super().__init__(message)


class BasePlugin(ABC):
    """Abstract base class for all plugins."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.metadata: PluginMetadata | None = None
        self._is_initialized = False
        self._is_active = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        pass

    @abstractmethod
    async def activate(self) -> bool:
        """Activate the plugin."""
        pass

    @abstractmethod
    async def deactivate(self) -> bool:
        """Deactivate the plugin."""
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        """Clean up plugin resources."""
        pass

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate plugin configuration."""
        return True  # Default implementation

    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        return self._is_initialized

    @property
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self._is_active


class ComponentPlugin(BasePlugin):
    """Base class for component plugins."""

    @abstractmethod
    def create_component(self, **kwargs) -> Any:
        """Create a component instance."""
        pass

    @abstractmethod
    def get_component_schema(self) -> dict[str, Any]:
        """Get component schema definition."""
        pass


class ProcessorPlugin(BasePlugin):
    """Base class for processor plugins."""

    @abstractmethod
    async def process(self, data: Any, context: dict[str, Any]) -> Any:
        """Process data with this plugin."""
        pass

    @abstractmethod
    def get_supported_types(self) -> list[str]:
        """Get list of supported data types."""
        pass


class ValidatorPlugin(BasePlugin):
    """Base class for validator plugins."""

    @abstractmethod
    def validate(self, data: Any, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate data against schema."""
        pass

    @abstractmethod
    def get_validation_rules(self) -> dict[str, Any]:
        """Get available validation rules."""
        pass


class ConnectorPlugin(BasePlugin):
    """Base class for connector plugins."""

    @abstractmethod
    async def connect(self, connection_config: dict[str, Any]) -> bool:
        """Establish connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection health."""
        pass


class MiddlewarePlugin(BasePlugin):
    """Base class for middleware plugins."""

    @abstractmethod
    async def before_request(self, request: Any, context: dict[str, Any]) -> Any:
        """Process request before main handler."""
        pass

    @abstractmethod
    async def after_request(self, response: Any, context: dict[str, Any]) -> Any:
        """Process response after main handler."""
        pass

    @abstractmethod
    async def on_error(self, error: Exception, context: dict[str, Any]) -> Any:
        """Handle errors in middleware."""
        pass


class PluginRegistry:
    """Central registry for managing plugins."""

    def __init__(self):
        self.plugins: dict[str, BasePlugin] = {}
        self.metadata: dict[str, PluginMetadata] = {}
        self.plugin_types: dict[PluginType, list[str]] = {plugin_type: [] for plugin_type in PluginType}
        self.dependencies: dict[str, list[str]] = {}
        self.hooks: dict[str, list[Callable]] = {}

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin with the registry."""
        try:
            metadata = plugin.get_metadata()
            plugin_name = metadata.name

            if plugin_name in self.plugins:
                logger.warning("Plugin %s is already registered", plugin_name)
                return False

            # Validate dependencies
            if not self._validate_dependencies(metadata.dependencies):
                msg = f"Plugin {plugin_name} has unmet dependencies"
                raise PluginError(msg, plugin_name)

            # Store plugin and metadata
            self.plugins[plugin_name] = plugin
            self.metadata[plugin_name] = metadata
            plugin.metadata = metadata

            # Update type mapping
            self.plugin_types[metadata.plugin_type].append(plugin_name)

            # Store dependencies
            if metadata.dependencies:
                self.dependencies[plugin_name] = metadata.dependencies

            logger.info("Plugin %s registered successfully", plugin_name)
            return True

        except Exception as e:
            logger.error("Failed to register plugin: %s", e)
            return False

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin from the registry."""
        if plugin_name not in self.plugins:
            logger.warning("Plugin %s is not registered", plugin_name)
            return False

        try:
            # Check for dependent plugins
            dependents = self._get_dependent_plugins(plugin_name)
            if dependents:
                msg = f"Cannot unregister plugin {plugin_name}: dependent plugins {dependents}"
                raise PluginError(msg, plugin_name)

            plugin = self.plugins[plugin_name]
            metadata = self.metadata[plugin_name]

            # Deactivate and cleanup
            if plugin.is_active:
                asyncio.create_task(plugin.deactivate())
            asyncio.create_task(plugin.cleanup())

            # Remove from registry
            del self.plugins[plugin_name]
            del self.metadata[plugin_name]

            # Update type mapping
            self.plugin_types[metadata.plugin_type].remove(plugin_name)

            # Remove dependencies
            if plugin_name in self.dependencies:
                del self.dependencies[plugin_name]

            logger.info("Plugin %s unregistered successfully", plugin_name)
            return True

        except Exception as e:
            logger.error("Failed to unregister plugin %s: %s", plugin_name, e)
            return False

    def get_plugin(self, plugin_name: str) -> BasePlugin | None:
        """Get a registered plugin by name."""
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: PluginType) -> list[BasePlugin]:
        """Get all plugins of a specific type."""
        plugin_names = self.plugin_types.get(plugin_type, [])
        return [self.plugins[name] for name in plugin_names]

    def get_active_plugins(self) -> list[BasePlugin]:
        """Get all active plugins."""
        return [plugin for plugin in self.plugins.values() if plugin.is_active]

    def list_plugins(self) -> dict[str, PluginMetadata]:
        """List all registered plugins with metadata."""
        return self.metadata.copy()

    def _validate_dependencies(self, dependencies: list[str]) -> bool:
        """Validate that plugin dependencies are met."""
        for dep in dependencies:
            if dep not in self.plugins:
                logger.error("Dependency %s not found", dep)
                return False
        return True

    def _get_dependent_plugins(self, plugin_name: str) -> list[str]:
        """Get list of plugins that depend on the given plugin."""
        dependents = []
        for name, deps in self.dependencies.items():
            if plugin_name in deps:
                dependents.append(name)
        return dependents

    def add_hook(self, hook_name: str, callback: Callable) -> None:
        """Add a hook callback for plugin events."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    def remove_hook(self, hook_name: str, callback: Callable) -> bool:
        """Remove a hook callback."""
        if hook_name in self.hooks and callback in self.hooks[hook_name]:
            self.hooks[hook_name].remove(callback)
            return True
        return False

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """Trigger all callbacks for a hook."""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error("Hook callback failed for %s: %s", hook_name, e)


class PluginManager:
    """Main plugin management system."""

    def __init__(self, plugin_dirs: list[str | Path] | None = None):
        self.registry = PluginRegistry()
        self.plugin_dirs = [Path(d) for d in plugin_dirs or []]
        self.auto_discover = True
        self.config_cache: dict[str, dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize the plugin manager."""
        if self.auto_discover:
            await self.discover_plugins()

        logger.info("Plugin manager initialized with %d plugins", len(self.registry.plugins))

    async def discover_plugins(self) -> list[str]:
        """Discover plugins in configured directories."""
        discovered = []

        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                logger.warning("Plugin directory does not exist: %s", plugin_dir)
                continue

            for python_file in plugin_dir.glob("**/*.py"):
                if python_file.name.startswith("__"):
                    continue

                try:
                    plugin_name = await self._load_plugin_from_file(python_file)
                    if plugin_name:
                        discovered.append(plugin_name)
                except Exception as e:
                    logger.error("Failed to load plugin from %s: %s", python_file, e)

        logger.info("Discovered %d plugins", len(discovered))
        return discovered

    async def _load_plugin_from_file(self, file_path: Path) -> str | None:
        """Load a plugin from a Python file."""
        try:
            # Construct module name from file path
            module_name = file_path.stem

            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find plugin classes in the module
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj != BasePlugin and not inspect.isabstract(obj):
                    # Create plugin instance
                    plugin = obj()

                    # Register the plugin
                    if self.registry.register_plugin(plugin):
                        metadata = plugin.get_metadata()
                        metadata.module_path = str(file_path)
                        return metadata.name

            return None

        except Exception as e:
            logger.error("Error loading plugin from %s: %s", file_path, e)
            return None

    async def load_plugin(self, plugin_name: str, config: dict[str, Any] | None = None) -> bool:
        """Load and initialize a specific plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            logger.error("Plugin %s not found", plugin_name)
            return False

        try:
            # Apply configuration
            if config:
                if plugin.validate_config(config):
                    plugin.config.update(config)
                    self.config_cache[plugin_name] = config
                else:
                    msg = f"Invalid configuration for plugin {plugin_name}"
                    raise PluginError(msg, plugin_name)

            # Initialize plugin
            if await plugin.initialize():
                plugin._is_initialized = True
                if plugin.metadata:
                    plugin.metadata.status = PluginStatus.INITIALIZED

                self.registry.trigger_hook("plugin_loaded", plugin_name, plugin)
                logger.info("Plugin %s loaded successfully", plugin_name)
                return True
            else:
                logger.error("Failed to initialize plugin %s", plugin_name)
                return False

        except Exception as e:
            logger.error("Error loading plugin %s: %s", plugin_name, e)
            if plugin.metadata:
                plugin.metadata.status = PluginStatus.ERROR
            return False

    async def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            logger.error("Plugin %s not found", plugin_name)
            return False

        if not plugin.is_initialized:
            logger.error("Plugin %s is not initialized", plugin_name)
            return False

        try:
            if await plugin.activate():
                plugin._is_active = True
                if plugin.metadata:
                    plugin.metadata.status = PluginStatus.ACTIVE

                self.registry.trigger_hook("plugin_activated", plugin_name, plugin)
                logger.info("Plugin %s activated successfully", plugin_name)
                return True
            else:
                logger.error("Failed to activate plugin %s", plugin_name)
                return False

        except Exception as e:
            logger.error("Error activating plugin %s: %s", plugin_name, e)
            if plugin.metadata:
                plugin.metadata.status = PluginStatus.ERROR
            return False

    async def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin."""
        plugin = self.registry.get_plugin(plugin_name)
        if not plugin:
            logger.error("Plugin %s not found", plugin_name)
            return False

        try:
            if await plugin.deactivate():
                plugin._is_active = False
                if plugin.metadata:
                    plugin.metadata.status = PluginStatus.INACTIVE

                self.registry.trigger_hook("plugin_deactivated", plugin_name, plugin)
                logger.info("Plugin %s deactivated successfully", plugin_name)
                return True
            else:
                logger.error("Failed to deactivate plugin %s", plugin_name)
                return False

        except Exception as e:
            logger.error("Error deactivating plugin %s: %s", plugin_name, e)
            return False

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin (deactivate, unregister, discover, load, activate)."""
        logger.info("Reloading plugin %s", plugin_name)

        # Get current configuration
        config = self.config_cache.get(plugin_name)

        # Deactivate if active
        plugin = self.registry.get_plugin(plugin_name)
        if plugin and plugin.is_active:
            await self.deactivate_plugin(plugin_name)

        # Unregister plugin
        self.registry.unregister_plugin(plugin_name)

        # Rediscover and load
        await self.discover_plugins()

        if await self.load_plugin(plugin_name, config):
            return await self.activate_plugin(plugin_name)

        return False

    def get_plugin_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all plugins."""
        status = {}

        for name, metadata in self.registry.metadata.items():
            plugin = self.registry.get_plugin(name)
            status[name] = {
                "metadata": {
                    "name": metadata.name,
                    "version": metadata.version,
                    "type": metadata.plugin_type.value,
                    "status": metadata.status.value,
                    "dependencies": metadata.dependencies,
                },
                "runtime": {
                    "initialized": plugin.is_initialized if plugin else False,
                    "active": plugin.is_active if plugin else False,
                    "config_loaded": name in self.config_cache,
                },
            }

        return status

    async def shutdown(self) -> None:
        """Shutdown all plugins and cleanup."""
        logger.info("Shutting down plugin manager")

        # Deactivate all active plugins
        for plugin in self.registry.get_active_plugins():
            if plugin.metadata:
                await self.deactivate_plugin(plugin.metadata.name)

        # Cleanup all plugins
        for plugin in self.registry.plugins.values():
            await plugin.cleanup()

        logger.info("Plugin manager shutdown complete")


# Global plugin manager instance
plugin_manager = PluginManager()


# Convenience functions
async def register_plugin(plugin: BasePlugin) -> bool:
    """Register a plugin."""
    return plugin_manager.registry.register_plugin(plugin)


async def load_plugin(plugin_name: str, config: dict[str, Any] | None = None) -> bool:
    """Load and initialize a plugin."""
    return await plugin_manager.load_plugin(plugin_name, config)


async def activate_plugin(plugin_name: str) -> bool:
    """Activate a plugin."""
    return await plugin_manager.activate_plugin(plugin_name)


def get_plugin(plugin_name: str) -> BasePlugin | None:
    """Get a plugin by name."""
    return plugin_manager.registry.get_plugin(plugin_name)


def get_plugins_by_type(plugin_type: PluginType) -> list[BasePlugin]:
    """Get all plugins of a specific type."""
    return plugin_manager.registry.get_plugins_by_type(plugin_type)


def add_plugin_hook(hook_name: str, callback: Callable) -> None:
    """Add a plugin event hook."""
    plugin_manager.registry.add_hook(hook_name, callback)


def get_plugin_status() -> dict[str, dict[str, Any]]:
    """Get status of all plugins."""
    return plugin_manager.get_plugin_status()
