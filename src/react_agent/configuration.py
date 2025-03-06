"""Define the configurable parameters for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Annotated, Literal, Optional

from langchain_core.runnables import RunnableConfig, ensure_config

from react_agent import prompts, tools, utils

# A singleton object to store the agent's configuration.
# We use this to store the schema for the agent's configuration, which
# needs to be generated dynamically based on the available tools.
APP_STATE = utils.State()


def create_configurable(toolbox: tools.Toolbox) -> None:
    """Dynamically create a configuration schema for the agent.

    This function will create a dataclass that represents the configuration schema.
    It will automatically include the names of the available tools in the schema.
    """
    # We need to save the tool names in the APP_STATE configuration schema
    # to make the type information available when generating
    # the json schema for the configuration.
    APP_STATE.tool_names = toolbox.get_tool_names()

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
            Literal[
                "anthropic/claude-3-7-sonnet-latest",
                "anthropic/claude-3-5-haiku-latest",
                "openai/o1",
                "openai/gpt-4o-mini",
                "openai/o1-mini",
                "openai/o3-mini",
            ],
            {"__template_metadata__": {"kind": "llm"}},
        ] = field(
            default="claude-3-5-haiku-latest",
            metadata={
                "description": (
                    "The name of the language model to use for the agent's "
                    "main interactions."
                    "Should be in the form: provider/model-name."
                )
            },
        )

        max_search_results: int = field(
            default=10,
            metadata={
                "description": (
                    "The maximum number of search results to "
                    "return for each search query."
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
