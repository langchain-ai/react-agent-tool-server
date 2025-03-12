"""Define the configurable parameters for the agent."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass, field, fields
from typing import Annotated, Literal, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

from react_agent import prompts, tools, utils

# A singleton object to store the agent's configuration.
# We use this to store the schema for the agent's configuration, which
# needs to be generated dynamically based on the available tools.
APP_STATE = utils.State()

PROVIDER_SECRET_PACKAGE = [
    ("openai", "OPENAI_API_KEY", "langchain_openai"),
    ("anthropic", "ANTHROPIC_API_KEY", "langchain_anthropic"),
]


def identify_available_model_providers() -> list[str]:
    """Determine which model providers are available."""
    available_providers = []
    for provider, secret, package in PROVIDER_SECRET_PACKAGE:
        if not os.environ.get(secret):
            continue

        if not importlib.util.find_spec(package):
            continue

        available_providers.append(provider)

    if not available_providers:
        providers = ", ".join([p for p, _, _ in PROVIDER_SECRET_PACKAGE])

        msg = (
            "Could not use any chat models. You must install the appropriate package "
            "and set the required environment variables.\n"
            f"You can use any of the following providers: {providers}\n"
            "To do that you will need to install the package and set the required "
            "environment variables."
        )

        for provider, secret, package in PROVIDER_SECRET_PACKAGE:
            msg += (
                f"\n\nFor {provider} models, install the package '{package}' "
                f"and set the environment variable '{secret}'."
            )

        raise ValueError(msg)

    return available_providers


PROVIDER_TO_MODELS = {
    "openai": ["openai/gpt-4o-mini", "openai/o3-mini"],
    "anthropic": [
        "anthropic/claude-3-7-sonnet-latest",
        "anthropic/claude-3-5-haiku-latest",
    ],
}


def get_available_models() -> list[str]:
    """Get the available models for the given providers."""
    available_models = []
    providers = identify_available_model_providers()
    for provider in providers:
        available_models.extend(PROVIDER_TO_MODELS[provider])
    return available_models


def create_configurable(toolbox: tools.Toolbox) -> None:
    """Dynamically create a configuration schema for the agent.

    This function will create a dataclass that represents the configuration schema.
    It will automatically include the names of the available tools in the schema.
    """
    # We need to save the tool names in the APP_STATE configuration schema
    # to make the type information available when generating
    # the json schema for the configuration.
    APP_STATE.tool_names = toolbox.get_tool_names()
    AVAILABLE_MODELS = get_available_models()
    if len(AVAILABLE_MODELS) < 1:
        raise ValueError("No models available for the agent.")
    APP_STATE.available_model_names = AVAILABLE_MODELS

    @dataclass(kw_only=True)
    class Config:
        """The configuration for the agent."""

        system_prompt: str = field(
            default=prompts.SYSTEM_PROMPT,
            metadata={
                "description": "The system prompt to use for the agent's interactions. "
                "This prompt sets the context and behavior for the agent."
            },
        )

        model: Annotated[
            Literal[*APP_STATE.available_model_names,],
            {"__template_metadata__": {"kind": "llm"}},
        ] = field(
            default=APP_STATE.available_model_names[0],
            metadata={
                "description": (
                    "The name of the language model to use for the agent's "
                    "main interactions."
                    "Should be in the form: provider/model-name."
                )
            },
        )

        selected_tools: list[Literal[*APP_STATE.tool_names]] = field(
            default_factory=list,
            metadata={
                "description": "The list of tools to use for the agent's interactions. "
                "This list should contain the names of the tools to use."
            },
        )

        @classmethod
        def from_runnable_config(
            cls, config: Optional[RunnableConfig] = None
        ) -> Config:
            """Create a Configuration instance from a RunnableConfig object."""
            config = ensure_config(config)
            configurable = config.get("configurable") or {}
            _fields = {f.name for f in fields(cls) if f.init}
            return cls(**{k: v for k, v in configurable.items() if k in _fields})

    APP_STATE.configurable = Config
