"""Define the configurable parameters for the agent."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from react_agent.configuration import create_configurable
from react_agent.tools import TOOLBOX


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the tools."""
    await TOOLBOX.initialize()
    create_configurable(TOOLBOX)
    yield


app = FastAPI(lifespan=lifespan)
