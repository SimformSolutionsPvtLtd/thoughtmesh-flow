"""Agno VectorDB integration."""

import pkgutil
from importlib import import_module
from typing import Any

import agno.vectordb as _vectordbs_pkg


class AgnoVectorDBLoader:
    """Loader for Agno vector DBs."""

    @staticmethod
    def get_vectordb(name: str, **kwargs) -> Any:
        """Retrieve an Agno vector database by name with given parameters."""
        module = import_module(f"agno.vectordb.{name.lower()}")
        vectordb_cls = getattr(module, name)
        return vectordb_cls(**kwargs)

    @staticmethod
    def list_vectordbs() -> list[str]:
        """List available Agno vector DB implementations by scanning agno.vectordb package."""
        return [name for _, name, _ in pkgutil.iter_modules(_vectordbs_pkg.__path__)]
