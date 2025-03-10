"""This module provides example tools for web scraping and search functionality."""

import os

from langchain_core.tools import BaseTool
from open_tool_client import AsyncClient, get_async_client


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
