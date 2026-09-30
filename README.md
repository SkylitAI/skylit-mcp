# Skylit MCP

<!-- MCP Registry badge: add after ai.skylit/mcp is published to the official MCP Registry. -->

Skylit is the data intelligence platform for AI trading: options flow,
volatility, dealer positioning and dark pool data for US markets.
The Skylit MCP server gives any MCP client (Claude, ChatGPT, Cursor, VS Code,
Gemini CLI, Codex and others) 63 read-only tools over that data.

This repository holds setup guides for each client, the Claude Code plugin, a
Gemini CLI extension, an agent skill, and runnable examples. It contains no
server code; the server is hosted by Skylit.

> **Status: beta.** The API and MCP server are open to Skylit members with API
> access. Check yours on the [Developer page](https://app.skylit.ai/developer).

## Quick connect

| | |
| --- | --- |
| **URL** | `https://mcp.skylit.ai/mcp` |
| **Transport** | Streamable HTTP |
| **Auth** | Sign in with Skylit (OAuth): add the URL and approve on the Skylit page. Or send `Authorization: Bearer <API key>` with a key from the [Developer page](https://app.skylit.ai/developer). |

Claude Code:

```bash
claude mcp add --transport http skylit https://mcp.skylit.ai/mcp
# then /mcp -> skylit -> Authenticate
```

Cursor, LM Studio, Warp and other clients that use an `mcpServers` JSON file:

```json
{
  "mcpServers": {
    "skylit": {
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer YOUR_SKYLIT_API_KEY" }
    }
  }
}
```

Leave out `headers` to sign in with Skylit instead. Field names differ between
clients (`url`, `httpUrl`, `serverUrl`, `servers`), so check your client below.

Then ask: *"What are the key gamma levels and today's flow tone for SPY?"*

## Clients

| Client | Sign in with Skylit | API key | Guide |
| --- | :-: | :-: | --- |
| Claude (claude.ai, Desktop, mobile) | Yes | Desktop, via `mcp-remote` | [clients/claude.md](clients/claude.md) |
| Claude Code | Yes | Yes | [clients/claude-code.md](clients/claude-code.md) |
| Cursor | Yes | Yes | [clients/cursor.md](clients/cursor.md) |
| VS Code / GitHub Copilot | Yes | Yes | [clients/vscode.md](clients/vscode.md) |
| Windsurf | Yes | Yes | [clients/windsurf.md](clients/windsurf.md) |
| Cline | Not documented | Yes | [clients/cline.md](clients/cline.md) |
| Zed | Yes | Yes | [clients/zed.md](clients/zed.md) |
| Gemini CLI | Yes | Yes | [clients/gemini-cli.md](clients/gemini-cli.md) |
| Codex CLI | Yes | Yes | [clients/codex-cli.md](clients/codex-cli.md) |
| ChatGPT (developer mode) | Yes | No | [clients/chatgpt.md](clients/chatgpt.md) |
| Goose | Yes | Yes | [clients/goose.md](clients/goose.md) |
| LM Studio | Yes | Yes | [clients/lm-studio.md](clients/lm-studio.md) |
| Raycast | Yes (untested) | Yes (untested) | [clients/raycast.md](clients/raycast.md) |
| Continue | Not documented | Yes | [clients/continue.md](clients/continue.md) |
| Warp | Yes | Yes | [clients/warp.md](clients/warp.md) |
| Perplexity | Yes (unverified) | Yes (unverified) | [clients/perplexity.md](clients/perplexity.md) |
| Any other MCP client, `mcp-remote`, MCP Inspector, raw HTTP | Yes | Yes | [clients/generic.md](clients/generic.md) |

"Sign in with Skylit" and "API key" reflect each client's own documentation as
of 2026-09-30. Guides mark anything we could not confirm.

## Tools

63 tools, all read-only. Each wraps one Skylit REST endpoint with the same
credit cost. Full catalog with arguments and prices:
[www.skylit.ai/docs/mcp/tools](https://www.skylit.ai/docs/mcp/tools).

| Family | Tools |
| --- | --- |
| **Discovery** | `flow_search`, `list_active_underlyings`, `expirations` |
| **Options flow and scores** | `flow_feed`, `trade_score`, `aggregate_score`, `flow_aggregate` |
| **Sweeps and momentum** | `sweeps`, `flow_momentum`, `flow_baseline` |
| **Strike and tide concentration** | `flow_strikes`, `flow_tide`, `by_strike` |
| **Screeners** | `top_underlyings_daily`, `top_underlyings_weekly`, `top_contracts_daily`, `top_contracts_weekly`, `unusual_volume`, `unusual_oi` |
| **Bull/bear and pressure** | `chain_bull_bear`, `contract_bull_bear`, `chain_ratio`, `contract_ratio` |
| **Stats, history, Vol/OI, moneyness** | `underlying_stats`, `underlying_bulk_stats`, `contract_bulk_stats`, `underlying_history`, `contract_history`, `flow_historical_compare`, `contract_stats`, `vol_oi`, `moneyness` |
| **Chain analytics and charts** | `option_chain`, `underlying_chart`, `contract_chart`, `underlying_rvol`, `contract_rvol` |
| **Market-wide and sector** | `market_overview`, `market_tide`, `market_breadth`, `sector_flow` |
| **Dark pool** | `dark_pool_trades`, `dark_pool_top_prints` |
| **Gamma/vanna heatmaps and key levels** | `heat_levels`, `heat_heatmap`, `heat_historical_heatmap` (point-in-time replay with `at`, up to 365 days back), `heat_stats_daily`, `heat_symbols` |
| **Tempest volatility suite** | `tempest_iv`, `tempest_term`, `tempest_cones`, `tempest_sigma`, `tempest_surface`, `tempest_tilt`, `tempest_events`, `tempest_snapshot`, `tempest_market`, `tempest_screener`, `tempest_history`, `tempest_derived`, `tempest_status`, `tempest_symbols` |
| **Account** | `account_usage` |

Tempest tools depend on your plan; without access they return `not_entitled`
at no charge. OHLCV price bars (Atlas) are available over REST, not MCP.

## Pricing

- Calls spend API credits: **1 credit = $0.001**. A typical call costs 1 to 5 credits.
- **Failed calls are free**: any `4xx` or `5xx` is refunded.
- **`account_usage` is free** and returns your balance and limits. Each tool
  result's `meta` includes the remaining balance.
- Per-tool costs: [tool catalog](https://www.skylit.ai/docs/mcp/tools).
  Plans and included credits: [www.skylit.ai/pricing](https://www.skylit.ai/pricing).

## REST API

The same data is available over REST with the same key. Each host serves its
OpenAPI spec at `/v1/openapi.json`:

| Host | Data |
| --- | --- |
| `https://api.skylit.ai` | Dealer positioning (Heatseeker), volatility (Tempest), options flow and dark pool (Flowseeker), account |
| `https://flow-api.skylit.ai` | Options flow and dark pool (alias for the Flowseeker paths) |
| `https://atlas-api.skylit.ai` | OHLCV price bars (Atlas) |

See [examples/python/rest-quickstart](examples/python/rest-quickstart) and the
[API reference](https://www.skylit.ai/docs/api-reference/introduction).

## What's in this repo

| Path | Purpose |
| --- | --- |
| [`clients/`](clients) | Setup guide per MCP client |
| [`plugins/claude-code/`](plugins/claude-code) and [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | Claude Code plugin: `/plugin marketplace add SkylitAI/skylit-mcp`, then `/plugin install skylit@skylit` |
| [`gemini-extension.json`](gemini-extension.json) and [`GEMINI.md`](GEMINI.md) | Gemini CLI extension: `gemini extensions install https://github.com/SkylitAI/skylit-mcp` |
| [`skills/skylit/`](skills/skylit/SKILL.md) | Agent skill on using the tools well: `npx skills add SkylitAI/skylit-mcp` |
| [`examples/`](examples) | Research agents: OpenAI Agents SDK, LangChain/LangGraph, Claude Agent SDK, Vercel AI SDK, plain REST |
| [`server.json`](server.json) | Official MCP Registry entry (`ai.skylit/mcp`) |
| [`llms-install.md`](llms-install.md) | Install steps for AI coding agents (Cline) |

The examples are research agents. They read data and never place orders; order
execution is left to your own broker.

## Data and licensing

- **This repository** (code and docs) is MIT licensed. See [LICENSE](LICENSE)
  and [NOTICE](NOTICE). The license does not cover Skylit data.
- **Skylit data** is governed by the [API Terms](https://www.skylit.ai/api-terms).
  Keys are personal. Using data for your own trading, research and education,
  including private agents that act for you, is covered. Commercial use,
  redistribution and republishing bulk data need a written license: contact
  [support@skylit.ai](mailto:support@skylit.ai).
- Skylit data is market information, not investment advice.

## Links

- Docs: [www.skylit.ai/docs](https://www.skylit.ai/docs)
  ([MCP overview](https://www.skylit.ai/docs/mcp/overview),
  [quickstart](https://www.skylit.ai/docs/mcp/quickstart),
  [example prompts](https://www.skylit.ai/docs/mcp/examples))
- Full agent reference (REST, streams, MCP): [www.skylit.ai/docs/skill.md](https://www.skylit.ai/docs/skill.md)
- API keys: [app.skylit.ai/developer](https://app.skylit.ai/developer)
- Support: [support@skylit.ai](mailto:support@skylit.ai)
- Security: [SECURITY.md](SECURITY.md)
- Legal: [Terms](https://www.skylit.ai/terms), [Privacy](https://www.skylit.ai/privacy), [API Terms](https://www.skylit.ai/api-terms)
