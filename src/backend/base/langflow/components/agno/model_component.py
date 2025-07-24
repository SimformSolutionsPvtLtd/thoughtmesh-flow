"""Agno Model component for LangFlow."""

from langflow.base.models.model import LCModelComponent
from langflow.field_typing import LanguageModel
from langflow.inputs.inputs import BoolInput, DropdownInput, FloatInput, IntInput, SecretStrInput, StrInput
from langflow.logging import logger


class AgnoModelComponent(LCModelComponent):
    display_name = "Agno Model"
    description = "Generates text using Agno models."
    icon = "Agno"
    name = "AgnoModel"

    inputs = [
        *LCModelComponent._base_inputs,
        DropdownInput(
            name="model_type",
            display_name="Model Type",
            options=["openai", "anthropic", "gemini", "ollama", "openai_like"],
            value="openai",
            info="Type of model provider",
            required=True,
        ),
        StrInput(
            name="model_id",
            display_name="Model ID",
            info="Model ID (e.g., gpt-4o, claude-3-5-sonnet-20241022, gemini-2.0-flash-exp)",
            value="gpt-4o",
            required=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            info="API key for the model provider",
            required=False,
        ),
        StrInput(
            name="base_url",
            display_name="Base URL",
            info="Base URL for API requests (for OpenAI-like providers)",
            required=False,
            advanced=True,
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            info="Controls randomness in output (0.0 to 2.0)",
            value=0.7,
            required=False,
            advanced=True,
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Tokens",
            info="Maximum number of tokens to generate",
            required=False,
            advanced=True,
        ),
        BoolInput(
            name="stream",
            display_name="Stream",
            value=False,
            info="Enable streaming responses",
            advanced=True,
        ),
        FloatInput(
            name="timeout",
            display_name="Timeout",
            value=60.0,
            info="Request timeout in seconds",
            advanced=True,
        ),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        try:
            # Import Agno model classes
            # from agno.models.anthropic import Claude
            # from agno.models.google import Gemini
            # from agno.models.ollama import Ollama
            from agno.models.openai import OpenAIChat
            # from agno.models.openai.like import OpenAILike

            # Model mapping
            model_map = {
                "openai": OpenAIChat,
                # "anthropic": Claude,
                # "gemini": Gemini,
                # "ollama": Ollama,
                # "openai_like": OpenAILike,
            }

            # Get model class
            model_class = model_map.get(self.model_type)
            if not model_class:
                error_msg = f"Unsupported model type: {self.model_type}"
                raise ValueError(error_msg)

            # Prepare model kwargs
            model_kwargs = {"id": self.model_id}

            # Add optional parameters
            if self.api_key:
                model_kwargs["api_key"] = self.api_key
            if self.base_url and self.model_type in ["openai_like", "openai"]:
                model_kwargs["base_url"] = self.base_url
            if self.temperature is not None:
                model_kwargs["temperature"] = self.temperature
            if self.max_tokens is not None:
                model_kwargs["max_tokens"] = self.max_tokens
            if self.timeout is not None:
                model_kwargs["timeout"] = self.timeout

            # Create and return model instance
            return model_class(**model_kwargs)

        except ImportError as exc:
            logger.error(f"Agno library not installed: {exc}")
            error_msg = "Agno library is required. Install with: pip install agno"
            raise ValueError(error_msg) from exc
        except Exception as exc:
            logger.error(f"Error creating Agno model: {exc}")
            raise
