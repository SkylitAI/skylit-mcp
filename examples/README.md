# Examples

Minimal research agents that answer questions like *"What are the key gamma
levels and today's flow tone for SPY?"* with Skylit data. Each one reads your
key from the `SKYLIT_API_KEY` environment variable and pins its dependencies.

| Example | Stack | Needs |
| --- | --- | --- |
| [python/openai-agents](python/openai-agents) | OpenAI Agents SDK, `MCPServerStreamableHttp` | `OPENAI_API_KEY` |
| [python/langchain](python/langchain) | `langchain-mcp-adapters` + LangChain `create_agent` (LangGraph) | `OPENAI_API_KEY` |
| [python/claude-agent-sdk](python/claude-agent-sdk) | Claude Agent SDK, remote MCP over HTTP | `ANTHROPIC_API_KEY` |
| [typescript/vercel-ai-sdk](typescript/vercel-ai-sdk) | AI SDK `createMCPClient` + `generateText` | `OPENAI_API_KEY` |
| [python/rest-quickstart](python/rest-quickstart) | Plain `requests` against the REST API | nothing else |

All examples are read-only: they fetch data and never place orders. Order
execution is left to your own broker.

Each run spends a few Skylit credits (1 credit = $0.001; failed calls are free).
Use your own key: under the [API Terms](https://www.skylit.ai/api-terms?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=examples-readme),
keys are personal and must not be built into software other people use.
