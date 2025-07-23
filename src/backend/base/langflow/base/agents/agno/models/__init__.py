"""Agno Models integration."""

from importlib import import_module
from typing import Any


class AgnoModelLoader:
    """Loader for Agno models."""

    @staticmethod
    def get_model(name: str, **kwargs) -> Any:
        """Retrieve an Agno model by name with given parameters."""
        module = import_module(f"langflow.base.agents.agno.models.{name.lower()}")
        model_cls = getattr(module, name)
        return model_cls(**kwargs)

    @staticmethod
    def list_models() -> list[str]:
        """List available Agno model names by scanning the agno.models package."""
        try:
            pkg = import_module("langflow.base.agents.agno.models")
            import pkgutil

            return [name for _, name, _ in pkgutil.iter_modules(pkg.__path__)]
        except ImportError:
            return []
