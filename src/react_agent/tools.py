"""This module provides example tools for web scraping and search functionality."""

import os

from langchain_core.tools import BaseTool
from universal_tool_client import AsyncClient, get_async_client


class Toolbox:
    """A container for managing and accessing LangChain tools.

    This class handles the initialization and retrieval of tools from a remote tool server.
    """

    def __init__(self, client: AsyncClient) -> None:
        """Initialize the Toolbox with an AsyncClient.

        Args:
            client: The AsyncClient instance used to communicate with the tool server.
        """
        self.tools = []
        self.client = client

    async def initialize(self) -> None:
        """Asynchronously fetch and initialize the tools from the remote server."""
        self.tools = await self.client.tools.as_langchain_tools()

    def get_tool_names(self) -> list[str]:
        """Get a list of names of all available tools.

        Returns:
            A list of tool names as strings.
        """
        return [tool.name for tool in self.tools]

    def get_tools(self) -> list[BaseTool]:
        """Get all available tools.

        Returns:
            A list of BaseTool instances.
        """
        return self.tools


TOOL_SERVER_URL = os.getenv("TOOL_SERVER_URL")

if not TOOL_SERVER_URL:
    raise ValueError("TOOL_SERVER_URL environment variable must be set")


TOOL_SERVER_API_KEY = os.getenv("TOOL_SERVER_API_KEY")

if not TOOL_SERVER_API_KEY:
    raise ValueError("TOOL_SERVER_API_KEY environment variable must be set")

TOOLBOX = Toolbox(
    client=get_async_client(
        url=TOOL_SERVER_URL,
        headers={
            "Authorization": TOOL_SERVER_API_KEY,
        },
    )
)
