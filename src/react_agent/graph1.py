import os
from oxp import Oxp
from typing import Callable, Awaitable, Any, TypedDict, Optional
from langchain_core.tools import StructuredTool
from langgraph.config import get_config
from datetime import UTC, datetime

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.types import interrupt
import json

from react_agent.utils import load_chat_model
from react_agent.prompts import SYSTEM_PROMPT

client = Oxp(
    bearer_token=os.environ.get("OXP_BEARER_TOKEN"),  # This is the default and can be omitted
)

client.health.check()

tools = client.tools.list()
available_tools = tools.items
available_tools_by_name = {tool.name: tool.dict() for tool in available_tools}
tool_ids = list(available_tools_by_name)


class HumanInterruptConfig(TypedDict):
    allow_ignore: bool
    allow_respond: bool
    allow_edit: bool
    allow_accept: bool


class ActionRequest(TypedDict):
    action: str
    args: dict

class HumanInterrupt(TypedDict):
    action_request: ActionRequest
    config: HumanInterruptConfig
    description: Optional[str]

def create_tool_caller(tool_name_: str) -> Callable[..., Awaitable[Any]]:
    """Create a tool caller."""

    def call_tool(**kwargs: Any) -> Any:
        """Call a tool."""
        config = get_config()
        user_id = config['configurable']['langgraph_auth_user_id']
        try:
            call_tool_result = client.tools.call(
                request={
                    "tool_id": tool_name_,
                    "context": {
                        "user_id": user_id,
                    },
                    "input": kwargs,
                },
            )
            call_tool_result = call_tool_result.dict()
        except Exception as eg:
            if hasattr(eg, "body"):
                body = eg.body
                if 'missing_requirements' in body:
                    missing_req = body['missing_requirements']
                    if 'authorization' in missing_req:
                        authorization = missing_req['authorization']
                        if len(authorization) == 1:
                            auth = authorization[0]
                            if 'authorization_url' in auth:

                                interrupt([{
                                    "action_request": {"action": "Auth", "args": {"url": auth['authorization_url']}},
                                    "config": {"allow_ignore": False, "allow_respond": False, "allow_edit": False, "allow_accept": True},
                                    "description": None
                                }])

            raise eg
        if not call_tool_result["success"]:
            raise NotImplementedError(
                "An error occurred while calling the tool. "
                "The client does not yet support error handling. "
                f"Info: {call_tool_result}"
            )
        return call_tool_result["value"]

    return call_tool


tools = []

for tool_id in tool_ids:
    tool_spec = available_tools_by_name[tool_id]

    tools.append(
        StructuredTool(
            name=tool_spec["name"],
            description=tool_spec["description"],
            args_schema=tool_spec["input_schema"],
            func=create_tool_caller(tool_id),
        )
    )
async def make_graph(config: RunnableConfig) -> CompiledStateGraph:
    """Create a custom state graph for the Reasoning and Action agent."""
    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model("openai/o3-mini")

    # Format the system prompt. Customize this to change the agent's behavior.
    prompt = SYSTEM_PROMPT.format(
        system_time=datetime.now(tz=UTC).isoformat()
    )
    tool_node = ToolNode(tools=tools)

    graph = create_react_agent(
        model, tools=tool_node, prompt=prompt
    )
    graph.name = "ReAct Agent"  # This customizes the name in LangSmith
    return graph