"""Agno Agent component for LangFlow."""

from typing import Any

from langflow.base.agents.agent import LCAgentComponent
from langflow.inputs.inputs import BoolInput, DropdownInput, HandleInput, MultilineInput, StrInput
from langflow.logging import logger


def convert_langchain_to_agno_model(llm: Any) -> Any:
    """Convert a LangChain LLM to an Agno-compatible model.

    Args:
        llm: A LangChain LLM object.

    Returns:
        An Agno-compatible model object.
    """
    try:
        from agno.models.anthropic import Claude
        from agno.models.google import Gemini
        from agno.models.ollama import Ollama
        from agno.models.openai import OpenAIChat
    except ImportError as exc:
        error_msg = "Agno library is required. Install with: pip install agno"
        raise ImportError(error_msg) from exc

    if not llm:
        return None

    # Get model name
    if hasattr(llm, "model_name") and llm.model_name:
        model_name = llm.model_name
    elif hasattr(llm, "model") and llm.model:
        model_name = llm.model
    elif hasattr(llm, "deployment_name") and llm.deployment_name:
        model_name = llm.deployment_name
    else:
        error_msg = "Could not find model name in the LLM object"
        raise ValueError(error_msg)

    # Get provider from namespace
    provider = llm.get_lc_namespace()[0] if hasattr(llm, "get_lc_namespace") else "unknown"

    # Remove langchain_ prefix if present
    provider = provider.removeprefix("langchain_")

    # Find API key
    api_key = None
    key_patterns = ["key", "token"]
    for attr in dir(llm):
        attr_lower = attr.lower()
        if any(pattern in attr_lower for pattern in key_patterns):
            value = getattr(llm, attr, None)
            if isinstance(value, str) and value:
                api_key = value
                break

    # Map providers to Agno model classes
    model_kwargs = {"id": model_name}
    if api_key:
        model_kwargs["api_key"] = api_key

    if provider in ["openai", "azure_openai"]:
        return OpenAIChat(**model_kwargs)
    if provider == "anthropic":
        return Claude(**model_kwargs)
    if provider in ["google", "gemini"]:
        return Gemini(**model_kwargs)
    if provider == "ollama":
        return Ollama(**model_kwargs)

    # Default to OpenAI for unknown providers
    logger.warning(f"Unknown provider '{provider}', defaulting to OpenAI")
    return OpenAIChat(**model_kwargs)


class AgnoAgentComponent(LCAgentComponent):
    display_name = "Agno Agent"
    description = "Instantiate an Agno agent using the official Agno library."
    icon = "Agno"
    name = "AgnoAgent"

    inputs = [
        StrInput(
            name="name",
            display_name="Agent Name",
            info="Name for the agent",
            value="Agno Agent",
            required=False,
        ),
        HandleInput(
            name="model",
            display_name="Model",
            input_types=["LanguageModel"],
            info="Language model to use for the agent",
            required=True,
        ),
        MultilineInput(
            name="description",
            display_name="Description",
            info="Description of the agent that is added to the system message",
            advanced=True,
        ),
        MultilineInput(
            name="instructions",
            display_name="Instructions",
            info="Instructions for the agent behavior",
            advanced=True,
        ),
        DropdownInput(
            name="tools",
            display_name="Tools",
            options=["duckduckgo", "yfinance", "calculator", "none"],
            value="none",
            info="Select tools to add to the agent",
            advanced=True,
        ),
        BoolInput(
            name="markdown",
            display_name="Use Markdown",
            value=True,
            info="Whether to use markdown formatting",
            advanced=True,
        ),
        BoolInput(
            name="show_tool_calls",
            display_name="Show Tool Calls",
            value=False,
            info="Show tool calls in the response",
            advanced=True,
        ),
    ]

    def build_agent(self) -> Any:
        try:
            # Import Agno components
            from agno.agent import Agent

            # Convert LangChain model to Agno model
            model = convert_langchain_to_agno_model(self.model)
            if not model:
                error_msg = "Model is required to create an Agno agent"
                raise ValueError(error_msg)

            # Load tools
            tool_list = []
            if self.tools and self.tools != "none":
                try:
                    if self.tools == "duckduckgo":
                        from agno.tools.duckduckgo import DuckDuckGoTools

                        tool_list.append(DuckDuckGoTools())
                    elif self.tools == "yfinance":
                        from agno.tools.yfinance import YFinanceTools

                        tool_list.append(YFinanceTools())
                    elif self.tools == "calculator":
                        from agno.tools.calculator import CalculatorTools

                        tool_list.append(CalculatorTools())
                except ImportError as exc:
                    logger.warning(f"Could not import tool '{self.tools}': {exc}")

            # Create agent
            agent_kwargs = {
                "model": model,
                "tools": tool_list if tool_list else None,
                "markdown": self.markdown,
                "show_tool_calls": self.show_tool_calls,
            }

            if self.name:
                agent_kwargs["name"] = self.name
            if self.description:
                agent_kwargs["description"] = self.description
            if self.instructions:
                agent_kwargs["instructions"] = [self.instructions]

            return Agent(**agent_kwargs)

        except ImportError as exc:
            logger.error(f"Agno library not installed: {exc}")
            error_msg = "Agno library is required. Install with: pip install agno"
            raise ValueError(error_msg) from exc
        except Exception as exc:
            logger.error(f"Error creating Agno agent: {exc}")
            raise
