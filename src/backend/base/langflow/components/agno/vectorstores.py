"""Agno VectorStores component for LangFlow."""

from typing import Any

from langflow.base.agents.agno.vectordbs import AgnoVectorDBLoader
from langflow.base.vectorstores.model import LCVectorStoreComponent, check_cached_vector_store
from langflow.inputs.inputs import (
    BoolInput,
    DropdownInput,
    IntInput,
    SecretStrInput,
    StrInput,
)


class AgnoVectorStoreComponent(LCVectorStoreComponent):
    display_name = "Agno Vector DB"
    description = "Store and search embeddings using Agno vector DBs."
    icon = "Agno"
    name = "AgnoVectorDB"

    inputs = [
        DropdownInput(
            name="vectordb_name",
            display_name="Vector DB Name",
            options=AgnoVectorDBLoader.list_vectordbs(),
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

    @check_cached_vector_store
    def build_vector_store(self) -> Any:
        return AgnoVectorDBLoader.get_vectordb(
            self.vectordb_name,
            api_key=self.api_key,
            endpoint=self.endpoint,
            stream=self.stream,
            timeout=self.timeout,
        )
