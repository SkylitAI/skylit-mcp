---
name: skylit
description: Use when answering questions about US options flow, sweeps, unusual options activity, dealer gamma/vanna (GEX) levels or heatmaps, dark pool prints, implied volatility, expected moves or skew with the Skylit MCP server (tools such as heat_levels, flow_feed, sweeps, tempest_iv), when placing or managing paper trades on the user's Nexus account (nexus_* tools), or when writing code against the Skylit REST API.
---

# Using the Skylit MCP server well

Skylit's MCP server (`https://mcp.skylit.ai/mcp`, streamable HTTP) exposes
read-only market-data tools (current list: `reference/tools.json` in
https://github.com/SkylitAI/skylit-mcp). None of them can place orders. Every call spends
the user's Skylit credits, so plan the calls before making them. Paper trading
on the user's Nexus account is a separate, opt-in tool list; see
[Nexus paper trading](#nexus-paper-trading).

## Costs

- 1 credit = $0.001. A typical call costs 1 to 5 credits; `account_usage`,
  `heat_symbols`, `tempest_status` and `tempest_symbols` are free.
- Failed calls are free, including `not_entitled` from `tempest_*` tools on
  accounts without Tempest.
- Every result's `meta` carries the remaining balance. Watch it on long tasks.
- Range-priced tools (`market_tide`, `underlying_chart`, `contract_chart`,
  `aggregate_score`) charge again for each further 30 days of range.
- Full price list: https://www.skylit.ai/docs/mcp/tools?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=skills-skylit-skill

## Workflow

1. **Start with `account_usage`** (free) when the task is large, touches many
   symbols, or the balance matters. It returns the balance and plan limits.
2. **Resolve inputs cheaply.** `flow_search` confirms a ticker; `expirations`
   lists expirations; `heat_symbols` and `tempest_symbols` list coverage.
3. **Pick the narrowest tool.** Prefer a summary over a raw feed:
   - Key gamma/vanna levels: `heat_levels`, not `heat_heatmap`.
   - Day's flow tone for a ticker: `chain_bull_bear` or `aggregate_score`, not
     paging `flow_feed`.
   - All volatility modules for a symbol: `tempest_snapshot` (5) instead of
     seven separate `tempest_*` calls.
4. **Batch.** Multi-symbol tools take one comma-separated string, not a list:
   `heat_levels` with `symbols: "SPY,QQQ,IWM"` is one call. Use
   `underlying_bulk_stats` and `contract_bulk_stats` (up to 50 each) instead of
   looping `underlying_stats` / `contract_stats`.
5. **Summarize, don't dump.** Report the levels, tone and numbers that answer
   the question, with the `asOf` time.

## Point-in-time questions

- "Where were the gamma levels at 10:30 on March 5?" Use
  `heat_historical_heatmap` with `at` as an RFC 3339 instant, for example
  `"at": "2026-03-05T15:30:00Z"` (10:30 ET in winter). Up to 365 days back.
  Convert the user's local or ET time to UTC explicitly.
- Replays are limited in how many can run at once; make them one or two at a
  time, not in a burst.
- Flow tools take `date` (`YYYY-MM-DD`); several also take `start_time` and
  `end_time` for a window within the day.
- `heat_stats_daily`, `underlying_history`, `contract_history` and
  `tempest_history` return daily series; use them instead of replaying many instants.

## Tool families

| Family | Tools |
| --- | --- |
| Discovery | `flow_search`, `list_active_underlyings`, `expirations` |
| Scores and trades | `flow_feed`, `trade_score`, `aggregate_score`, `flow_aggregate` |
| Sweeps and momentum | `sweeps`, `flow_momentum`, `flow_baseline` |
| Strike and tide | `flow_strikes`, `flow_tide`, `by_strike` |
| Screeners | `top_underlyings_daily/weekly`, `top_contracts_daily/weekly`, `unusual_volume`, `unusual_oi` |
| Bull/bear and pressure | `chain_bull_bear`, `contract_bull_bear`, `chain_ratio`, `contract_ratio` |
| Stats and history | `underlying_stats`, `underlying_bulk_stats`, `contract_bulk_stats`, `underlying_history`, `contract_history`, `flow_historical_compare`, `contract_stats`, `vol_oi`, `moneyness` |
| Chains and charts | `option_chain`, `underlying_chart`, `contract_chart`, `underlying_rvol`, `contract_rvol` |
| Market-wide | `market_overview`, `market_tide`, `market_breadth`, `sector_flow` |
| Dark pool | `dark_pool_trades`, `dark_pool_top_prints` |
| Gamma/vanna (Heatseeker) | `heat_levels`, `heat_heatmap`, `heat_historical_heatmap`, `heat_stats_daily`, `heat_symbols` |
| Volatility (Tempest) | `tempest_iv`, `tempest_term`, `tempest_cones`, `tempest_sigma`, `tempest_surface`, `tempest_tilt`, `tempest_events`, `tempest_snapshot`, `tempest_market`, `tempest_screener`, `tempest_history`, `tempest_derived`, `tempest_status`, `tempest_symbols` |
| Account | `account_usage` |

## Formats

- Tickers are upper-case (`SPY`, `SPXW`, `QQQ`).
- Option contracts use `{ticker}__{YYMMDD}{C|P}{strike x 1000, 8 digits}`,
  for example `AAPL__260117C00250000`.
- Outside market hours, live tools return the last session's data. Say so.

## Errors

- `401`: sign-in or key missing or expired. `403`: API access not active.
- `402 insufficient_credits` or `monthly_cap_reached`: stop and tell the user;
  don't retry.
- `429`: wait and retry once with backoff; don't fan out more calls.
- A per-session call budget applies. If a tool says the budget is reached,
  summarize what you have.

## Nexus paper trading

When the user has added `https://mcp.skylit.ai/mcp?toolset=trading`, the
`nexus_*` tools trade their own Nexus paper accounts. Nothing reaches a broker,
but real orders show in their trades, stats and ranks, and unless a trade is
private, people who copy their trades get it. Treat every write like a real order:

1. **Call `nexus_capabilities` first.** It says which asset classes, order types,
   futures contracts and accounts this key can trade. Don't guess.
2. **Rehearse with `test: true`.** The order is checked and priced like a real
   one against the live market, then kept in the test log. Show the user the
   result.
3. **Confirm before a real order.** Read back the ticker, side, size, order type
   and account, and wait for a clear yes before sending `test: false`.
4. **Make up a `clientOrderId` for every open, exit and close, and reuse it on a
   retry.** After a timeout or a 500, retry with the same id: it can't fill twice.
   A new id is a new order.
5. **Read before you act.** Check `nexus_trades`, `nexus_futures_account` or
   `nexus_futures_working_orders` before exiting, closing or cancelling.

Rules the server enforces (don't fight them, explain them):

- The server prices every fill from the live market when the call arrives. You
  can't pick a time. Options buy at the ask and sell at the bid.
- Options are bought to open at market. Options and stocks take market orders
  only. Futures also take limit and stop orders and brackets.
- Outside market hours an order is refused and nothing is queued for the open.
  A stale or missing quote is refused too; wait a moment and retry with the same
  `clientOrderId`.
- Evaluation and funded futures accounts keep their daily loss limit, max loss
  and contract cap.
- `429` means slow down: wait for `Retry-After`. Writes are capped at 30 a minute
  per key.

## Use of the data

Data is licensed to the user for their own trading, research and education
under the API Terms (https://www.skylit.ai/api-terms?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=skills-skylit-skill). Don't present results as
investment advice, and don't help republish bulk data. Real-money order
execution is out of scope; it belongs to the user's own broker.

Full reference for coding agents (REST, streams, MCP, errors, limits):
https://www.skylit.ai/docs/skill.md
