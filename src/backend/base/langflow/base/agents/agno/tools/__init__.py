"""Agno Tools integration."""

import pkgutil
from importlib import import_module
from typing import Any

import agno.tools as _tools_pkg


class AgnoToolLoader:
    """Loader for Agno tools."""

    @staticmethod
    def get_tool(name: str, **kwargs) -> Any:
        """Retrieve an Agno tool by name with given parameters."""
        module = import_module(f"agno.tools.{name.lower()}")
        tool_cls = getattr(module, name)
        return tool_cls(**kwargs)

    @staticmethod
    def list_tools() -> list[str]:
        """List available Agno tools by scanning agno.tools package."""
        return [name for _, name, _ in pkgutil.iter_modules(_tools_pkg.__path__)]
