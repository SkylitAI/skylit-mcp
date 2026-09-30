# Claude Agent SDK

Runs a [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) agent with the Skylit MCP server over HTTP. Built-in tools (shell, files, web) are turned off and the allow-list is `mcp__skylit`, so the agent can do nothing but read Skylit data.

Read-only research agent: it answers questions with Skylit data and never places
orders. Order execution is left to your own broker.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export SKYLIT_API_KEY="..."     # https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=examples-python-claude-agent-sdk-readme
export ANTHROPIC_API_KEY="..."
python main.py "What are the key gamma levels and today's flow tone for SPY?"
```

Requires Python 3.10+. The SDK bundles the Claude Code CLI it drives.
