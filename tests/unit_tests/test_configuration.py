from langchain_core.tools import tool
from universal_tool_client import get_async_client

from react_agent.configuration import APP_STATE, create_configurable
from react_agent.tools import Toolbox


@tool
def echo(text: str) -> str:
    """Echo the input text."""
    return text


async def test_configuration_empty() -> None:
    """Test creating a configuration with no tools."""
    toolbox = Toolbox(get_async_client(url="http://localhost:8080"))
    # Hard code the tools
    toolbox.tools = [echo]
    create_configurable(toolbox)
    assert APP_STATE.tool_names == ["echo"]
    assert hasattr(APP_STATE, "configurable")
