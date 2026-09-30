"""Research agent: LangChain MCP adapters + a LangGraph agent + the Skylit MCP server.

Read-only. It answers questions about market data and never places orders.

    export SKYLIT_API_KEY=...   # https://app.skylit.ai/developer
    export OPENAI_API_KEY=...
    python main.py "What are the key gamma levels and today's flow tone for SPY?"
"""

import asyncio
import os
import sys

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

SKYLIT_MCP_URL = "https://mcp.skylit.ai/mcp"
DEFAULT_QUESTION = "What are the key gamma levels and today's flow tone for SPY?"
MODEL = os.environ.get("MODEL", "openai:gpt-5.4-mini")

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

    client = MultiServerMCPClient(
        {
            "skylit": {
                "transport": "streamable_http",
                "url": SKYLIT_MCP_URL,
                "headers": {"Authorization": f"Bearer {api_key}"},
            }
        }
    )
    tools = await client.get_tools()

    # create_agent is LangChain 1.x's LangGraph-based agent; it replaces
    # langgraph.prebuilt.create_react_agent, which is deprecated in LangGraph 1.x.
    agent = create_agent(MODEL, tools=tools, system_prompt=SYSTEM_PROMPT)
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 16},
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
