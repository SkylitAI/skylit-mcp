"""Research agent: Claude Agent SDK + the Skylit MCP server.

Read-only. It answers questions about market data and never places orders.
Built-in tools (shell, files, web) are disabled; Skylit tools are the allow-list.

    export SKYLIT_API_KEY=...   # https://app.skylit.ai/developer
    export ANTHROPIC_API_KEY=...
    python main.py "What are the key gamma levels and today's flow tone for SPY?"
"""

import asyncio
import os
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

SKYLIT_MCP_URL = "https://mcp.skylit.ai/mcp"
DEFAULT_QUESTION = "What are the key gamma levels and today's flow tone for SPY?"

SYSTEM_PROMPT = """You are a market research assistant with read-only Skylit tools.
Keep credit use low: prefer heat_levels for gamma levels and chain_bull_bear for
the day's flow tone, and pass several symbols as one comma-separated string.
Report the numbers that answer the question and the time they are as of.
You cannot place trades. This is research, not investment advice."""


async def main() -> None:
    api_key = os.environ.get("SKYLIT_API_KEY")
    if not api_key:
        sys.exit("Set SKYLIT_API_KEY (create one at https://app.skylit.ai/developer).")
    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={
            "skylit": {
                "type": "http",
                "url": SKYLIT_MCP_URL,
                "headers": {"Authorization": f"Bearer {api_key}"},
            }
        },
        tools=[],  # no built-in tools
        allowed_tools=["mcp__skylit"],  # every Skylit tool, all read-only
        permission_mode="dontAsk",  # deny anything not allowed above
        max_turns=8,
    )

    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage) and message.is_error:
            sys.exit(f"Agent stopped: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
