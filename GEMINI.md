# Skylit market data

The `skylit` MCP server gives read-only US options market data: options flow and
scores, sweeps, screeners, chain analytics, dark pool prints, dealer gamma/vanna
heatmaps and key levels (with point-in-time replay), and the Tempest volatility
suite. It cannot place trades.

If a tool returns `401`, ask the user to run `/mcp auth skylit` and approve on
the Skylit page.

Each call spends the user's Skylit credits (1 credit = $0.001; failed calls are
free). Pick the narrowest tool that answers the question:

- `account_usage` (free) shows the balance and limits. Call it first before a large pull.
- `flow_search` resolves a ticker; `expirations` lists expirations.
- Dealer positioning: `heat_levels` for key levels, `heat_heatmap` for the full
  board, `heat_historical_heatmap` with `at` (RFC 3339) for a past instant.
- Flow: `chain_bull_bear` for the day's tone, `flow_feed`, `sweeps`, `flow_tide`,
  `unusual_volume`, `unusual_oi`, and the `top_*` screeners.
- Dark pool: `dark_pool_trades`, `dark_pool_top_prints`.
- Volatility: `tempest_*` tools. Accounts without Tempest get `not_entitled` at no charge.
- Several symbols go in one comma-separated string, for example `"SPY,QQQ"`.
- Option contracts use `{ticker}__{YYMMDD}{C|P}{strike x 1000, 8 digits}`,
  for example `AAPL__260117C00250000`.

Outside market hours, data reflects the last session. Data is licensed for the
user's own research; don't present it as investment advice.

Tool catalog with credit costs: https://www.skylit.ai/docs/mcp/tools
