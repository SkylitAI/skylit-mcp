# @skylitai/sdk

A TypeScript client for [Skylit](https://www.skylit.ai/?utm_source=npm&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-typescript-readme) market data. Skylit covers options flow, volatility, dealer positioning (GEX/vanna levels and point-in-time replay) and dark pool, and is built for AI trading agents and the people who build them.

It is typed, has no dependencies, and runs on Node 18+, Bun, Deno and edge runtimes. Market data calls are read-only. The Nexus trading calls place paper trades on your own Nexus account and never reach a broker (see below).

```bash
npm install @skylitai/sdk
export SKYLIT_API_KEY=...   # create one at https://app.skylit.ai/developer?utm_source=npm&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-typescript-readme
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

## Nexus paper trading

The same key trades your Nexus paper accounts through the Nexus Trades API: options and stocks in your paper wallet, futures in your practice, evaluation or funded account. The server prices every fill from the live market and runs the same account rules as Nexus. Order bodies use the API's field names.

```ts
await skylit.tradingCapabilities();                    // what this key can trade right now

await skylit.openTrade({ contract: "SPY 600C 10/16", quantity: 1, clientOrderId: "spy-call-1", test: true }); // rehearse first
await skylit.trades({ status: "open" });               // your open options and stock trades
await skylit.exitTrade(tradeId, { quantity: 1, clientOrderId: "spy-call-1-trim" });

await skylit.openTrade({ assetClass: "futures", ticker: "NQ", side: "buy", quantity: 1, clientOrderId: "nq-1", test: true });
await skylit.futuresAccount("practice");               // balance, positions, loss rules
await skylit.closeFutures("practice", { ticker: "NQ", clientOrderId: "nq-1-close", test: true });
```

- `test: true` checks and prices an order like a real one, then keeps it in your test log instead of placing it.
- Send a `clientOrderId` you make up and reuse it if you retry: you get the first order back and nothing new is placed.
- Futures resting orders: `futuresWorkingOrders`, `futuresOrder`, `cancelFuturesOrder`, `cancelFuturesOrders`, `modifyFuturesOrder`. History: `futuresOrders`.

## Agents

For Claude, ChatGPT, Cursor, the Vercel AI SDK, the OpenAI Agents SDK and other MCP clients, connect to the hosted MCP server at `MCP_URL` (`https://mcp.skylit.ai/mcp`). Setup guides for each client are at [SkylitAI/skylit-mcp](https://github.com/SkylitAI/skylit-mcp).

## Pricing and terms

Calls are billed in credits (1 credit = $0.001; most calls cost 1 to 5). See [the docs](https://www.skylit.ai/docs?utm_source=npm&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-typescript-readme). Use of Skylit data is governed by the [API Terms](https://www.skylit.ai/api-terms?utm_source=npm&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-typescript-readme), which cover personal and research use; for commercial use, contact support@skylit.ai. The MIT license covers this client's code, not Skylit data.

## Staying current

This client and [its repo](https://github.com/SkylitAI/skylit-mcp) are checked against the live API every 6 hours; new releases follow API changes.
