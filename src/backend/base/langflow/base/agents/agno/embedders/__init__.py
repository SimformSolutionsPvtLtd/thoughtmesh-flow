"""Agno Embedders integration."""

import pkgutil
from importlib import import_module
from typing import Any

import agno.embedder as _embedders_pkg


class AgnoEmbedderLoader:
    """Loader for Agno embedders."""

    @staticmethod
    def get_embedder(name: str, **kwargs) -> Any:
        """Retrieve an Agno embedder by name with given parameters."""
        module = import_module(f"agno.embedder.{name.lower()}")
        embedder_cls = getattr(module, name)
        return embedder_cls(**kwargs)

    @staticmethod
    def list_embedders() -> list[str]:
        """List available Agno embedders by scanning agno.embedder package."""
        return [name for _, name, _ in pkgutil.iter_modules(_embedders_pkg.__path__)]
