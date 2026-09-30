"""Research agent: OpenAI Agents SDK + the Skylit MCP server.

Read-only. It answers questions about market data and never places orders.

    export SKYLIT_API_KEY=...   # https://app.skylit.ai/developer
    export OPENAI_API_KEY=...
    python main.py "What are the key gamma levels and today's flow tone for SPY?"
"""

import asyncio
import os
import sys

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

SKYLIT_MCP_URL = "https://mcp.skylit.ai/mcp"
DEFAULT_QUESTION = "What are the key gamma levels and today's flow tone for SPY?"

INSTRUCTIONS = """You are a market research assistant with read-only Skylit tools.
Keep credit use low: prefer heat_levels for gamma levels and chain_bull_bear for
the day's flow tone, and pass several symbols as one comma-separated string.
Report the numbers that answer the question and the time they are as of.
You cannot place trades. This is research, not investment advice."""


async def main() -> None:
    api_key = os.environ.get("SKYLIT_API_KEY")
    if not api_key:
        sys.exit("Set SKYLIT_API_KEY (create one at https://app.skylit.ai/developer).")
    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION

    async with MCPServerStreamableHttp(
        name="skylit",
        params={
            "url": SKYLIT_MCP_URL,
            "headers": {"Authorization": f"Bearer {api_key}"},
            "timeout": 30,
        },
        cache_tools_list=True,
        client_session_timeout_seconds=30,
    ) as skylit:
        agent = Agent(
            name="Skylit research agent",
            instructions=INSTRUCTIONS,
            mcp_servers=[skylit],
        )
        result = await Runner.run(agent, question, max_turns=8)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
