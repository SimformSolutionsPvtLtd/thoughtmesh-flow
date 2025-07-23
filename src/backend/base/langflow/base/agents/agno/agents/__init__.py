"""Agno Agents integration."""

import pkgutil
from importlib import import_module
from typing import Any

import agno.agent as _agents_pkg


class AgnoAgentLoader:
    """Loader for Agno agents."""

    @staticmethod
    def get_agent(name: str, **kwargs) -> Any:
        """Retrieve an Agno agent by name with given parameters."""
        module = import_module(f"agno.agent.{name.lower()}")
        agent_cls = getattr(module, name)
        return agent_cls(**kwargs)

    @staticmethod
    def list_agents() -> list[str]:
        """List available Agno agent names by scanning agno.agent package."""
        return [name for _, name, _ in pkgutil.iter_modules(_agents_pkg.__path__)]
