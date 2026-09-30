# OpenAI Agents SDK

Connects an [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) agent to the Skylit MCP server with `MCPServerStreamableHttp`. The SDK runs the MCP client locally, so your Skylit key is sent to `mcp.skylit.ai` and nowhere else.

Read-only research agent: it answers questions with Skylit data and never places
orders. Order execution is left to your own broker.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export SKYLIT_API_KEY="..."     # https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=examples-python-openai-agents-readme
export OPENAI_API_KEY="..."
python main.py "What are the key gamma levels and today's flow tone for SPY?"
```

Requires Python 3.10+. The agent uses the SDK's default model; set `OPENAI_DEFAULT_MODEL` to change it.

Alternative: the SDK's `HostedMCPTool` has OpenAI's Responses API call the server for you. That sends your Skylit key to OpenAI as part of the tool config, so this example uses the local client.
