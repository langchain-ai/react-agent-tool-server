> [!IMPORTANT]  
> This is a work in progress.

# LangGraph ReAct Agent Template (WIP)

A template that deploys a ReAct agent with access to an [open-tool-server](https://github.com/langchain-ai/open-tool-server/).

## Getting Started

1. Deploy the Open Tool Server with configured tools.
2. Launch the ReAct agent with the `TOOL_SERVER_URL` environment variable set to the URL of the tool server.


### Development

Make sure that you also include any necessary environment variables related to models

```shell
TOOL_SERVER_URL=http://localhost:8000 uv run langgraph dev
```
