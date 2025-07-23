"""Agno toolkit loader for LangFlow integration."""


class AgnoToolkit:
    """Loader for Agno tools and utilities."""

    def __init__(self, api_key: str | None = None, endpoint: str | None = None):
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.agno.ai"

    def get_tools(self) -> list:
        """Retrieve a list of Agno tools for use by the agent."""
        # TODO: Implement actual tool loading logic
        return []
