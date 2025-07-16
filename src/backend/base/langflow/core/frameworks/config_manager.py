"""
Advanced Configuration Management System for Agno Framework Integration.

This module provides comprehensive configuration management, environment handling,
secrets management, and dynamic configuration updates for the Langflow-Agno integration.
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Union

import yaml

logger = logging.getLogger(__name__)


class ConfigSource(Enum):
    """Configuration source types."""

    FILE = "file"
    ENVIRONMENT = "environment"
    DATABASE = "database"
    API = "api"
    MEMORY = "memory"


class ConfigFormat(Enum):
    """Supported configuration formats."""

    JSON = "json"
    YAML = "yaml"
    TOML = "toml"
    INI = "ini"
    PROPERTIES = "properties"


@dataclass
class ConfigMetadata:
    """Metadata for configuration entries."""

    source: ConfigSource
    format: ConfigFormat | None = None
    last_modified: datetime = field(default_factory=datetime.now)
    checksum: str = ""
    encrypted: bool = False
    required: bool = False
    description: str = ""


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""

    def __init__(self, message: str, config_key: str | None = None):
        self.config_key = config_key
        super().__init__(message)


class ConfigValidator:
    """Configuration validation utilities."""

    @staticmethod
    def validate_type(value: Any, expected_type: type) -> bool:
        """Validate value type."""
        if expected_type == Union:
            return True  # Union types are always valid
        return isinstance(value, expected_type)

    @staticmethod
    def validate_range(value: float, min_val: float, max_val: float) -> bool:
        """Validate numeric range."""
        return min_val <= value <= max_val

    @staticmethod
    def validate_choices(value: Any, choices: list[Any]) -> bool:
        """Validate value is in allowed choices."""
        return value in choices

    @staticmethod
    def validate_pattern(value: str, pattern: str) -> bool:
        """Validate string pattern using regex."""
        import re

        return bool(re.match(pattern, value))


class SecretManager:
    """Secure secrets management."""

    def __init__(self, encryption_key: str | None = None):
        self.encryption_key = encryption_key
        self._secrets: dict[str, str] = {}

    def _encrypt(self, value: str) -> str:
        """Encrypt a secret value."""
        if not self.encryption_key:
            return value  # No encryption if no key provided

        # Simple encryption for demo - use proper encryption in production
        return base64.b64encode(value.encode()).decode()

    def _decrypt(self, encrypted_value: str) -> str:
        """Decrypt a secret value."""
        if not self.encryption_key:
            return encrypted_value  # No decryption if no key provided

        # Simple decryption for demo - use proper decryption in production
        try:
            return base64.b64decode(encrypted_value.encode()).decode()
        except (ValueError, UnicodeDecodeError):
            return encrypted_value  # Return original if decryption fails

    def store_secret(self, key: str, value: str) -> None:
        """Store an encrypted secret."""
        encrypted_value = self._encrypt(value)
        self._secrets[key] = encrypted_value
        logger.debug("Secret stored for key: %s", key)

    def get_secret(self, key: str) -> str | None:
        """Retrieve and decrypt a secret."""
        encrypted_value = self._secrets.get(key)
        if encrypted_value is None:
            return None

        return self._decrypt(encrypted_value)

    def delete_secret(self, key: str) -> bool:
        """Delete a secret."""
        if key in self._secrets:
            del self._secrets[key]
            logger.debug("Secret deleted for key: %s", key)
            return True
        return False

    def list_secret_keys(self) -> list[str]:
        """List all secret keys."""
        return list(self._secrets.keys())


class ConfigManager:
    """Advanced configuration management system."""

    def __init__(self, base_path: str | Path | None = None, encryption_key: str | None = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.secret_manager = SecretManager(encryption_key)

        # Configuration storage
        self._config: dict[str, Any] = {}
        self._metadata: dict[str, ConfigMetadata] = {}
        self._validators: dict[str, list[Callable]] = {}
        self._watchers: dict[str, list[Callable]] = {}

        # Default configuration paths
        self.config_paths = [
            self.base_path / "config" / "default.yaml",
            self.base_path / "config" / "config.yaml",
            self.base_path / ".env",
        ]

        # Environment-specific configurations
        env = os.getenv("ENVIRONMENT", "development")
        env_config = self.base_path / "config" / f"{env}.yaml"
        if env_config.exists():
            self.config_paths.append(env_config)

    def _calculate_checksum(self, data: str) -> str:
        """Calculate checksum for configuration data."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _parse_file(self, file_path: Path) -> tuple[dict[str, Any], ConfigFormat]:
        """Parse configuration file based on extension."""
        suffix = file_path.suffix.lower()

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if suffix in [".yaml", ".yml"]:
            data = yaml.safe_load(content) or {}
            return data, ConfigFormat.YAML
        elif suffix == ".json":
            data = json.loads(content)
            return data, ConfigFormat.JSON
        elif suffix in [".env", ".properties"]:
            data = self._parse_env_file(content)
            return data, ConfigFormat.PROPERTIES
        else:
            msg = f"Unsupported configuration format: {suffix}"
            raise ConfigurationError(msg)

    def _parse_env_file(self, content: str) -> dict[str, Any]:
        """Parse environment file format."""
        config = {}
        for line in content.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")

                    # Try to convert to appropriate type
                    if value.lower() in ["true", "false"]:
                        value = value.lower() == "true"
                    elif value.isdigit():
                        value = int(value)
                    elif self._is_float(value):
                        value = float(value)

                    config[key] = value
        return config

    def _is_float(self, value: str) -> bool:
        """Check if string represents a float."""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def load_from_file(self, file_path: str | Path) -> None:
        """Load configuration from a file."""
        file_path = Path(file_path)

        if not file_path.exists():
            logger.warning("Configuration file not found: %s", file_path)
            return

        try:
            config_data, config_format = self._parse_file(file_path)
            content = file_path.read_text(encoding="utf-8")
            checksum = self._calculate_checksum(content)

            metadata = ConfigMetadata(
                source=ConfigSource.FILE,
                format=config_format,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                checksum=checksum,
            )

            self._merge_config(config_data, metadata, str(file_path))
            logger.info("Loaded configuration from: %s", file_path)

        except Exception as e:
            msg = f"Failed to load configuration from {file_path}: {e}"
            raise ConfigurationError(msg) from e

    def load_from_environment(self, prefix: str = "LANGFLOW_") -> None:
        """Load configuration from environment variables."""
        env_config = {}

        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix) :].lower()

                # Convert nested keys (LANGFLOW_DB_HOST -> db.host)
                if "_" in config_key:
                    config_key = config_key.replace("_", ".")

                # Try to convert to appropriate type
                if value.lower() in ["true", "false"]:
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)

                env_config[config_key] = value

        if env_config:
            metadata = ConfigMetadata(source=ConfigSource.ENVIRONMENT, last_modified=datetime.now())

            self._merge_config(env_config, metadata, "environment")
            logger.info("Loaded %d configuration values from environment", len(env_config))

    def _merge_config(self, config_data: dict[str, Any], metadata: ConfigMetadata, source_info: str) -> None:
        """Merge configuration data into main config."""
        for key, value in config_data.items():
            # Handle nested configurations
            if isinstance(value, dict) and key in self._config and isinstance(self._config[key], dict):
                self._config[key].update(value)
            else:
                self._config[key] = value

            self._metadata[key] = metadata

            # Trigger watchers
            self._notify_watchers(key, value)

    def _notify_watchers(self, key: str, value: Any) -> None:
        """Notify configuration watchers of changes."""
        if key in self._watchers:
            for watcher in self._watchers[key]:
                try:
                    watcher(key, value)
                except Exception as e:
                    logger.error("Configuration watcher failed for key %s: %s", key, e)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default."""
        # Support nested keys (e.g., "db.host")
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        # Check if it's a secret reference
        if isinstance(value, str) and value.startswith("${SECRET:") and value.endswith("}"):
            secret_key = value[9:-1]  # Remove ${SECRET: and }
            secret_value = self.secret_manager.get_secret(secret_key)
            return secret_value if secret_value is not None else default

        return value

    def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.MEMORY) -> None:
        """Set configuration value."""
        # Validate the value if validators are registered
        self._validate_value(key, value)

        # Support nested keys
        keys = key.split(".")
        config = self._config

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

        # Update metadata
        self._metadata[key] = ConfigMetadata(source=source, last_modified=datetime.now())

        # Trigger watchers
        self._notify_watchers(key, value)

        logger.debug("Configuration set: %s = %s", key, value)

    def delete(self, key: str) -> bool:
        """Delete configuration value."""
        keys = key.split(".")
        config = self._config

        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                return False
            config = config[k]

        # Delete the value
        if keys[-1] in config:
            del config[keys[-1]]
            if key in self._metadata:
                del self._metadata[key]
            logger.debug("Configuration deleted: %s", key)
            return True

        return False

    def has(self, key: str) -> bool:
        """Check if configuration key exists."""
        return self.get(key, sentinel=object()) is not object()

    def get_all(self) -> dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()

    def get_metadata(self, key: str) -> ConfigMetadata | None:
        """Get metadata for a configuration key."""
        return self._metadata.get(key)

    def add_validator(self, key: str, validator: Callable[[Any], bool]) -> None:
        """Add a validator for a configuration key."""
        if key not in self._validators:
            self._validators[key] = []
        self._validators[key].append(validator)

    def _validate_value(self, key: str, value: Any) -> None:
        """Validate a configuration value."""
        if key not in self._validators:
            return

        for validator in self._validators[key]:
            if not validator(value):
                msg = f"Validation failed for configuration key '{key}' with value '{value}'"
                raise ConfigurationError(msg, key)

    def add_watcher(self, key: str, callback: Callable[[str, Any], None]) -> None:
        """Add a watcher for configuration changes."""
        if key not in self._watchers:
            self._watchers[key] = []
        self._watchers[key].append(callback)

    def remove_watcher(self, key: str, callback: Callable[[str, Any], None]) -> bool:
        """Remove a configuration watcher."""
        if key in self._watchers and callback in self._watchers[key]:
            self._watchers[key].remove(callback)
            return True
        return False

    def reload(self) -> None:
        """Reload configuration from all sources."""
        logger.info("Reloading configuration from all sources")

        # Clear current configuration
        old_config = self._config.copy()
        self._config.clear()
        self._metadata.clear()

        try:
            # Load from files
            for config_path in self.config_paths:
                if config_path.exists():
                    self.load_from_file(config_path)

            # Load from environment
            self.load_from_environment()

            logger.info("Configuration reloaded successfully")

        except Exception as e:
            # Restore old configuration on error
            self._config = old_config
            msg = f"Failed to reload configuration: {e}"
            raise ConfigurationError(msg) from e

    def save_to_file(self, file_path: str | Path, config_format: ConfigFormat = ConfigFormat.YAML) -> None:
        """Save current configuration to a file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if config_format == ConfigFormat.YAML:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(self._config, f, default_flow_style=False, indent=2)
            elif config_format == ConfigFormat.JSON:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, indent=2, default=str)
            else:
                msg = f"Unsupported save format: {config_format}"
                raise ConfigurationError(msg)

            logger.info("Configuration saved to: %s", file_path)

        except Exception as e:
            msg = f"Failed to save configuration to {file_path}: {e}"
            raise ConfigurationError(msg) from e

    def export_env_file(self, file_path: str | Path, prefix: str = "LANGFLOW_") -> None:
        """Export configuration as environment file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        def flatten_dict(d: dict, parent_key: str = "", separator: str = "_") -> dict:
            """Flatten nested dictionary."""
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, separator).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        try:
            flattened = flatten_dict(self._config)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"# Generated configuration file - {datetime.now()}\n\n")

                for key, value in flattened.items():
                    env_key = f"{prefix}{key.upper()}"
                    if isinstance(value, str):
                        f.write(f'{env_key}="{value}"\n')
                    else:
                        f.write(f"{env_key}={value}\n")

            logger.info("Environment file exported to: %s", file_path)

        except Exception as e:
            msg = f"Failed to export environment file to {file_path}: {e}"
            raise ConfigurationError(msg) from e

    def get_config_summary(self) -> dict[str, Any]:
        """Get configuration summary for monitoring."""
        summary = {
            "total_keys": len(self._config),
            "sources": {},
            "last_reload": datetime.now().isoformat(),
            "secrets_count": len(self.secret_manager.list_secret_keys()),
            "watchers_count": sum(len(watchers) for watchers in self._watchers.values()),
            "validators_count": sum(len(validators) for validators in self._validators.values()),
        }

        # Count by source
        for metadata in self._metadata.values():
            source = metadata.source.value
            summary["sources"][source] = summary["sources"].get(source, 0) + 1

        return summary


# Global configuration manager instance
config_manager = ConfigManager()


# Convenience functions for common operations
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value."""
    return config_manager.get(key, default)


def set_config(key: str, value: Any) -> None:
    """Set configuration value."""
    config_manager.set(key, value)


def has_config(key: str) -> bool:
    """Check if configuration key exists."""
    return config_manager.has(key)


def load_config(config_path: str | Path | None = None) -> None:
    """Load configuration from default or specified path."""
    if config_path:
        config_manager.load_from_file(config_path)
    else:
        config_manager.reload()


def store_secret(key: str, value: str) -> None:
    """Store a secret value."""
    config_manager.secret_manager.store_secret(key, value)


def get_secret(key: str) -> str | None:
    """Get a secret value."""
    return config_manager.secret_manager.get_secret(key)


def watch_config(key: str, callback: Callable[[str, Any], None]) -> None:
    """Watch for configuration changes."""
    config_manager.add_watcher(key, callback)


def validate_config(key: str, validator: Callable[[Any], bool]) -> None:
    """Add configuration validator."""
    config_manager.add_validator(key, validator)


# Configuration validation helpers
def require_config(key: str) -> Any:
    """Get required configuration value, raise error if missing."""
    value = get_config(key)
    if value is None:
        msg = f"Required configuration key '{key}' is missing"
        raise ConfigurationError(msg, key)
    return value


def get_database_config() -> dict[str, Any]:
    """Get database configuration with defaults."""
    return {
        "host": get_config("database.host", "localhost"),
        "port": get_config("database.port", 5432),
        "name": get_config("database.name", "langflow"),
        "user": get_config("database.user", "langflow"),
        "password": get_secret("database.password"),
        "pool_size": get_config("database.pool_size", 10),
        "max_overflow": get_config("database.max_overflow", 20),
    }


def get_redis_config() -> dict[str, Any]:
    """Get Redis configuration with defaults."""
    return {
        "host": get_config("redis.host", "localhost"),
        "port": get_config("redis.port", 6379),
        "db": get_config("redis.db", 0),
        "password": get_secret("redis.password"),
        "max_connections": get_config("redis.max_connections", 10),
    }


def get_agno_config() -> dict[str, Any]:
    """Get Agno framework configuration."""
    return {
        "enabled": get_config("agno.enabled", True),
        "api_key": get_secret("agno.api_key"),
        "base_url": get_config("agno.base_url", "https://api.agno.ai"),
        "timeout": get_config("agno.timeout", 30),
        "retry_attempts": get_config("agno.retry_attempts", 3),
        "batch_size": get_config("agno.batch_size", 100),
    }
