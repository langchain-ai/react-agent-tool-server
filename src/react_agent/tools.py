"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

import os

from langchain_core.tools import BaseTool
from langchain_tool_server.client import AsyncClient, get_async_client


class Toolbox:
    def __init__(self, client: AsyncClient) -> None:
        self.tools = []
        self.client = client

    async def initialize(self) -> None:
        self.tools = await self.client.tools.as_langchain_tools()

    def get_tool_names(self) -> list[str]:
        return [tool.name for tool in self.tools]

    def get_tools(self) -> list[BaseTool]:
        """Get tools."""
        return self.tools


TOOL_SERVER_URL = os.getenv("TOOL_SERVER_URL")

if not TOOL_SERVER_URL:
    raise ValueError("TOOL_SERVER_URL environment variable must be set")

TOOLBOX = Toolbox(client=get_async_client(url=TOOL_SERVER_URL))
