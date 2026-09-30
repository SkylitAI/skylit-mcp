# LangChain + LangGraph

Loads the Skylit MCP tools with [`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters) and runs them in a LangChain `create_agent` agent, which is built on LangGraph.

Read-only research agent: it answers questions with Skylit data and never places
orders. Order execution is left to your own broker.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export SKYLIT_API_KEY="..."     # https://app.skylit.ai/developer
export OPENAI_API_KEY="..."
python main.py "What are the key gamma levels and today's flow tone for SPY?"
```

Requires Python 3.10+. The model defaults to `openai:gpt-5.4-mini`; set `MODEL` to any LangChain model string (for example `anthropic:...` after `pip install langchain-anthropic`).

`create_agent` replaces `langgraph.prebuilt.create_react_agent`, which LangGraph 1.x marks deprecated. The tool loading is the same for both.
