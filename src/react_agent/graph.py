"""Create a ReAct agent with access to tools defined in a tool server."""

from datetime import UTC, datetime

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from react_agent.configuration import APP_STATE
from react_agent.tools import TOOLBOX
from react_agent.utils import load_chat_model


async def make_graph(config: RunnableConfig) -> CompiledStateGraph:
    """Create a custom state graph for the Reasoning and Action agent."""
    configuration = APP_STATE.configurable.from_runnable_config(config)

    tools_to_use = [
        tool
        for tool in TOOLBOX.get_tools()
        if tool.name in configuration.selected_tools or not configuration.selected_tools
    ]

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(configuration.model).bind_tools(tools_to_use)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = configuration.system_prompt.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )

    graph = create_react_agent(
        model, system_message, config_schema=APP_STATE.configurable
    )
    graph.name = "ReAct Agent"  # This customizes the name in LangSmith
    return graph
