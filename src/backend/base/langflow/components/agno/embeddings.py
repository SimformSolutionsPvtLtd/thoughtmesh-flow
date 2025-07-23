"""Agno Embeddings component for LangFlow."""

from langflow.base.agents.agno.embedders import AgnoEmbedderLoader
from langflow.base.embeddings.model import LCEmbeddingsModel
from langflow.field_typing import Embeddings
from langflow.inputs.inputs import (
    BoolInput,
    DropdownInput,
    IntInput,
    SecretStrInput,
    StrInput,
)


class AgnoEmbeddingsComponent(LCEmbeddingsModel):
    display_name = "Agno Embeddings"
    description = "Generate embeddings using Agno embedders."
    icon = "Agno"
    name = "AgnoEmbeddings"

    inputs = [
        DropdownInput(
            name="embedder_name",
            display_name="Embedder Name",
            options=AgnoEmbedderLoader.list_embedders(),
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="Agno API key",
            required=False,
        ),
        StrInput(
            name="endpoint",
            display_name="Endpoint",
            info="Agno API endpoint",
            value="https://api.agno.ai",
            required=False,
        ),
        BoolInput(
            name="stream",
            display_name="Stream",
            value=False,
            advanced=True,
        ),
        IntInput(
            name="timeout",
            display_name="Timeout",
            value=60,
            advanced=True,
        ),
    ]

    def build_embeddings(self) -> Embeddings:
        return AgnoEmbedderLoader.get_embedder(
            self.embedder_name,
            api_key=self.api_key,
            endpoint=self.endpoint,
            stream=self.stream,
            timeout=self.timeout,
        )
