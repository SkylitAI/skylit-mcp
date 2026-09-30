# @skylitai/sdk

A TypeScript client for [Skylit](https://www.skylit.ai) market data. Skylit covers options flow, volatility, dealer positioning (GEX/vanna levels and point-in-time replay) and dark pool, and is built for AI trading agents and the people who build them.

It is typed, has no dependencies, and runs on Node 18+, Bun, Deno and edge runtimes. Every call is read-only: it fetches data and never places orders.

```bash
npm install @skylitai/sdk
export SKYLIT_API_KEY=...   # create one at https://app.skylit.ai/developer
```

```ts
import { Skylit } from "@skylitai/sdk";

const skylit = new Skylit();

await skylit.account();                                // balance, prices, limits (free)
await skylit.gexLevels("SPY");                         // king node, gatekeepers, flip, walls
await skylit.historical("SPY", "2026-09-29T15:30:00Z"); // the board at a past instant
await skylit.vol("iv", ["SPY", "QQQ"]);                // Tempest implied volatility
await skylit.flowTone("TSLA");                         // bull/bear pressure across the chain
await skylit.get("/v1/vol/screener", { limit: 20 });   // any documented endpoint
```

Responses are the API's JSON, `{ data, meta }`. `meta` carries the remaining credits and the rate-limit state. Errors throw `SkylitError` with `status`, `code` and `message`. Failed calls are not charged.

## Agents

For Claude, ChatGPT, Cursor, the Vercel AI SDK, the OpenAI Agents SDK and other MCP clients, connect to the hosted MCP server at `MCP_URL` (`https://mcp.skylit.ai/mcp`). Setup guides for each client are at [SkylitAI/skylit-mcp](https://github.com/SkylitAI/skylit-mcp).

## Pricing and terms

Calls are billed in credits (1 credit = $0.001; most calls cost 1 to 5). See [the docs](https://www.skylit.ai/docs). Use of Skylit data is governed by the [API Terms](https://www.skylit.ai/api-terms), which cover personal and research use; for commercial use, contact support@skylit.ai. The MIT license covers this client's code, not Skylit data.

## Staying current

This client and [its repo](https://github.com/SkylitAI/skylit-mcp) are checked against the live API every 6 hours; new releases follow API changes.
