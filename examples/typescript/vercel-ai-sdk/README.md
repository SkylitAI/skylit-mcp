# Vercel AI SDK

Connects to the Skylit MCP server with the [AI SDK MCP client](https://ai-sdk.dev/docs/ai-sdk-core/mcp-tools)
(`createMCPClient` from `@ai-sdk/mcp`, HTTP transport) and answers a question
with `generateText`.

Read-only research agent: it answers questions with Skylit data and never places
orders. Order execution is left to your own broker.

## Run

```bash
npm ci

export SKYLIT_API_KEY="..."     # https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=examples-typescript-vercel-ai-sdk-readme
export OPENAI_API_KEY="..."
npm start -- "What are the key gamma levels and today's flow tone for SPY?"
```

Requires Node.js 22+. The model defaults to `gpt-5.4-mini`; set `MODEL` to
change it, or swap `@ai-sdk/openai` for another AI SDK provider.

`npm run typecheck` runs `tsc --noEmit`.
