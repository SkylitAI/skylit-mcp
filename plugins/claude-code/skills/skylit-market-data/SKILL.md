---
name: skylit-market-data
description: Use when the user asks about US options flow, sweeps, unusual options activity, dealer gamma/vanna (GEX) levels or heatmaps, dark pool prints, or implied volatility, expected moves and skew, and the Skylit MCP tools are available. Also use when writing code against the Skylit REST API.
---

# Using Skylit market data

The `skylit` MCP server (https://mcp.skylit.ai/mcp) exposes read-only tools. Each call
spends the user's Skylit API credits, so pick the narrowest tool that answers the question.

- Start with `account_usage` (free) if balance or plan limits matter.
- Resolve tickers with `flow_search`; list expirations with `expirations`.
- Dealer positioning: `heat_levels` for key levels, `heat_heatmap` for the full board,
  `heat_historical_heatmap` with `at` (RFC 3339) for a past instant.
- Options flow: `flow_feed`, `sweeps`, `flow_tide`, `unusual_volume`, `unusual_oi`, screeners (`top_*`).
- Dark pool: `dark_pool_trades`, `dark_pool_top_prints`.
- Volatility (plans with Tempest): `tempest_iv`, `tempest_cones`, `tempest_surface`, `tempest_market`.
  Without access these return `not_entitled` at no charge.
- Several symbols go in one comma-separated string, for example `"SPY,QQQ"`.
- Option contracts use `{ticker}__{YYMMDD}{C|P}{strike x 1000, 8 digits}`, e.g. `AAPL__260117C00250000`.
- Outside market hours, data is the last session's close. Results report remaining credits in `meta`.

Data is licensed for the user's own research. Do not present it as investment advice.

Full reference (REST, MCP, errors, limits): https://www.skylit.ai/docs/skill.md
Tool catalog with credit costs: https://www.skylit.ai/docs/mcp/tools?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=plugins-claude-code-skills-skylit-market-data-skill
