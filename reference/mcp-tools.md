# Tool Catalog

> Every Skylit MCP tool, grouped by purpose, with its credit cost.

> **Beta.** The API and MCP server are open to members with API access. Check yours on the [Developer page](https://app.skylit.ai/developer).

The server exposes the tools below. Each call costs the same credits as the
equivalent REST endpoint; the cost is shown per tool below and your remaining
balance is returned in each result's `meta`.

Every tool wraps a Skylit REST endpoint **1:1** — same auth, same credit cost,
same JSON. The **Arguments** column lists each tool's inputs; **bold** ones are
required. A tool takes the commonly used subset of its endpoint's parameters,
in snake_case (`max_strikes` on the `heat_*` tools is the REST `maxStrikes`).
The **Endpoint** column gives the underlying path; for each parameter's allowed
values and the response schema, see the
[API Reference](https://www.skylit.ai/docs/api-reference/introduction). For example, `flow_feed` is the
[`GET /v1/flow/{ticker}`](/docs/api-reference/flow/raw-flow-feed-for-a-ticker-flow-score-flowbonus-per-trade)
operation. The `heat_*` tools map to the Heatseeker endpoints, the `tempest_*` tools to the
Tempest `/v1/vol` endpoints, and everything else maps to Flowseeker. All are served on `api.skylit.ai`
(Flowseeker is also on its alias, `flow-api.skylit.ai`). Atlas isn't on the MCP server; its REST API
is on its own host, `https://atlas-api.skylit.ai`.

> **Info:** Tools that take a single option contract expect an **OPRA symbol** in URL-safe
> form: `{ticker}__{YYMMDD}{C|P}{strike×1000, 8 digits}` — e.g.
> `AAPL__260117C00250000`. Discover tickers with `flow_search` and expirations with
> `expirations` first.

> **Note:** **Arguments.** Tools that take several symbols (`symbols` on the `heat_*` tools,
> `tickers` on `dark_pool_trades`) take **one comma-separated string**, for example
> `"SPY,QQQ"`, not a JSON list.
>
> **Range-priced tools.** `market_tide`, `underlying_chart`, `contract_chart` and
> `aggregate_score` cost the listed price for the first 30 days of range and the
> same again for each further 30 days (for example `market_tide` with
> `interval=360D` costs 3 x 12 = 36 credits). The REST reference pages give the caps.
>
> **Tempest tools.** An account without Tempest access gets a `not_entitled`
> error from the `tempest_*` tools, which is free.

## Discovery

Find valid symbols and the active universe before calling analytics tools.

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `flow_search` | Search underlyings by ticker fragment | **`q`**, `limit` | `GET /v1/underlying/search` | 1 |
| `list_active_underlyings` | Every underlying that traded options on a date, ranked by premium | `date`, `limit`, `min_premium`, `min_volume` | `GET /v1/underlying` | 1 |
| `expirations` | Available expiration dates for an underlying, with contract counts | **`ticker`**, `date` | `GET /v1/underlying/{ticker}/expirations` | 1 |

## Scores & trades

Scored options flow for a ticker or a single trade.

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `flow_feed` | Recent scored trades (Flow Score, FlowBonus) + VWF/SDF/FIR aggregates | **`ticker`**, `date`, `limit`, `min_premium`, `moneyness`, `option_type`, `timeframe`, `trade_type` | `GET /v1/flow/{ticker}` | 1 |
| `trade_score` | Full scoring + context for one trade id (from a `flow_feed` row) | **`trade_id`** | `GET /v1/score/{trade_id}` | 1 |
| `aggregate_score` | Composite + VWF/SDF/FIR across one or more trailing timeframes | **`ticker`**, `date`, `include_breakdown`, `include_moneyness`, `timeframes` | `GET /v1/aggregate/{ticker}` | 3 |
| `flow_aggregate` | Server-side rollup over an arbitrary `[start_time, end_time]` window | **`ticker`**, **`start_time`**, **`end_time`**, `date`, `exclude_multi_leg`, `max_dte`, `min_dte`, `min_premium`, `option_type` | `GET /v1/flow/{ticker}/aggregate` | 3 |

## Sweeps & momentum

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `sweeps` | Aggregated multi-exchange sweeps with venues, premium, moneyness, score | **`ticker`**, `date`, `limit`, `min_premium`, `moneyness`, `option_type`, `timeframe` | `GET /v1/sweeps/{ticker}` | 3 |
| `flow_momentum` | Live 5m/30m/1h flow vs trailing baseline, with z-scores + trend label | **`ticker`**, `as_of`, `lookback_days` | `GET /v1/flow/{ticker}/momentum` | 3 |
| `flow_baseline` | Trailing per-time-of-day baseline `flow_momentum` compares against | **`ticker`**, `bucket`, `end_time_of_day`, `lookback_days`, `max_dte`, `min_dte`, `start_time_of_day` | `GET /v1/flow/{ticker}/baseline` | 3 |

## Strike & tide concentration

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `flow_strikes` | Top-N strikes by net/total premium with bull/bear split + OI context | **`ticker`**, **`start_time`**, **`end_time`**, `min_premium`, `order_by`, `right`, `top_n` | `GET /v1/flow/{ticker}/strikes` | 3 |
| `flow_tide` | Bucketed bullish vs bearish premium with cumulative net premium | **`ticker`**, **`start_time`**, **`end_time`**, `bucket`, `min_premium`, `option_type` | `GET /v1/flow/{ticker}/tide` | 3 |
| `by_strike` | Strike-level distribution of a day's flow, optionally by DTE band | **`ticker`**, `date`, `dte_filter`, `interval` | `GET /v1/underlying/{ticker}/by-strike` | 3 |

## Screeners

Single-day and weekly top lists, plus unusual-activity scanners.

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `top_underlyings_daily` | Top underlyings by single-day flow (call/put split, net premium, ratio) | `date`, `limit`, `min_premium`, `min_volume`, `order`, `order_by` | `GET /v1/underlying/top/daily` | 1 |
| `top_underlyings_weekly` | Same, over the trailing week | `date`, `limit`, `min_premium`, `min_volume`, `order`, `order_by` | `GET /v1/underlying/top/weekly` | 1 |
| `top_contracts_daily` | Single-day top-contract screener (premium / volume / OI / sweeps) | `date`, `limit`, `min_oi`, `min_premium`, `min_volume`, `only_sweeps`, `order`, `order_by`, `right`, `ticker` | `GET /v1/contract/top/daily` | 3 (1 with `ticker`) |
| `top_contracts_weekly` | Same, over the trailing week | `date`, `limit`, `min_oi`, `min_premium`, `min_volume`, `only_sweeps`, `order`, `order_by`, `right`, `ticker` | `GET /v1/contract/top/weekly` | 1 |
| `unusual_volume` | Contracts with anomalous volume vs an `avg_period` baseline (RVOL) | `avg_period`, `date`, `exclude_tickers`, `limit`, `min_premium`, `min_rvol`, `moneyness`, `order_by`, `right`, `ticker` | `GET /v1/contract/unusual-volume` | 3 |
| `unusual_oi` | Contracts with significant open-interest changes (opening vs closing) | `date`, `direction`, `limit`, `min_oi_change`, `min_oi_change_pct`, `order_by`, `right`, `ticker` | `GET /v1/contract/unusual-oi` | 3 |

## Bull/bear & pressure ratios

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `chain_bull_bear` | Chain-level bull/bear/neutral % with call- and put-only breakdowns | **`ticker`**, `date`, `min_premium`, `option_type`, `timeframe` | `GET /v1/chain-bull-bear/{ticker}` | 3 |
| `contract_bull_bear` | Bull/bear/neutral % for a single OPRA contract | **`symbol`**, `date`, `min_premium`, `timeframe` | `GET /v1/contract-bull-bear/{symbol}` | 1 |
| `chain_ratio` | Chain-level ask/bid/mid + aggression ratios with a bias interpretation | **`ticker`**, `date`, `max_dte`, `min_dte`, `min_premium`, `option_type`, `timeframe` | `GET /v1/chain-ratio/{ticker}` | 1 |
| `contract_ratio` | Same bid/ask/mid pressure for a single OPRA contract | **`symbol`**, `date`, `min_premium`, `timeframe` | `GET /v1/contract-ratio/{symbol}` | 1 |

## Stats, Vol/OI & moneyness

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `underlying_stats` | Daily aggregate stats for an underlying (premium, volume, net, OI) | **`ticker`**, `date` | `GET /v1/underlying/{ticker}/stats` | 1 |
| `underlying_bulk_stats` | One-day stats (premium, volume, call/put split, net premium) for up to 50 tickers in one call; tickers with no options activity are absent | **`tickers`**, `date` | `GET /v1/underlying/bulk/stats` | 5 |
| `contract_bulk_stats` | One-day stats for up to 50 option contracts (OPRA symbols) in one call | **`symbols`**, `date` | `GET /v1/contract/bulk/stats` | 5 |
| `underlying_history` | Daily options-flow history for a ticker, one row per trading day (premium, volume, call/put split, net premium) | **`ticker`**, **`start_date`**, **`end_date`** | `GET /v1/underlying/{ticker}/history` | 5 |
| `contract_history` | Daily history for one contract: premium, volume, OI change, bid/ask split, sweep and multi-leg share, VWAP, last price, IV, trade count | **`symbol`**, **`start_date`**, **`end_date`** | `GET /v1/contract/{symbol}/history` | 5 |
| `flow_historical_compare` | Today's flow vs its trailing 20-trading-day average: deltas, percentile ranks and the five most similar past days | **`ticker`**, `date` | `GET /v1/flow/{ticker}/historical-compare` | 5 |
| `contract_stats` | Daily aggregate stats for a contract (volume, OI, premium, IV) | **`symbol`**, `date` | `GET /v1/contract/{symbol}/stats` | 1 |
| `vol_oi` | Vol/OI accumulation analysis; distinguishes new positioning from closing | **`ticker`**, `date`, `min_oi`, `moneyness`, `option_type`, `timeframe` | `GET /v1/vol-oi/{ticker}` | 1 |
| `moneyness` | Premium/sentiment split across deep_itm…deep_otm + detected patterns | **`ticker`**, `date`, `min_premium`, `timeframe` | `GET /v1/moneyness/{ticker}` | 1 |

## Chains, charts & RVOL

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `option_chain` | Full chain at an expiration (per-strike call/put volume, OI, premium) | **`ticker`**, **`expiration`**, `date`, `min_volume` | `GET /v1/underlying/{ticker}/chain` | 3 |
| `underlying_chart` | Intraday OHLC-style bars for an underlying | **`ticker`**, **`interval`**, **`bucket`** | `GET /v1/underlying/{ticker}/chart` | 3 |
| `contract_chart` | Intraday OHLC-style bars for a single contract | **`symbol`**, **`interval`**, **`bucket`** | `GET /v1/contract/{symbol}/chart` | 3 |
| `underlying_rvol` | Relative-volume bars for an underlying (`format=summary` for stats only) | **`ticker`**, `avg_period`, `bucket`, `date`, `format`, `interval`, `limit`, `order`, `order_by` | `GET /v1/underlying/{ticker}/rvol` | 1 |
| `contract_rvol` | Relative-volume bars for a single contract | **`symbol`**, `avg_period`, `bucket`, `date`, `format`, `interval`, `limit`, `order`, `order_by` | `GET /v1/contract/{symbol}/rvol` | 1 |

## Market-wide & sector

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `market_overview` | Market-wide flow for the day + top tickers by premium | `tickers` | `GET /v1/market/overview` | 3 |
| `market_tide` | Bucketed net call/put premium time series with an SPY overlay | `bucket`, `date`, `exclude_deep_itm`, `exclude_multi_leg`, `interval` | `GET /v1/market/tide` | 3 |
| `market_breadth` | SPY/QQQ/IWM sentiment, advance/decline, per-sector rotation | `date`, `fir_threshold` | `GET /v1/flow/market-breadth` | 3 |
| `sector_flow` | Sector/industry flow aggregation with top-contributor tickers | **`sector`**, `date`, `top_n` | `GET /v1/flow/sector/{sector}` | 3 |

## Dark pool

Off-exchange (TRF) prints. No side / BBO / greeks — these are raw block prints.

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `dark_pool_trades` | Paginated off-exchange prints (filters: tickers / date range / notional / venue / sector); `$1M+` by default, span capped at 31 days | `date`, `date_end`, `date_start`, `limit`, `max_notional`, `min_notional`, `offset`, `order`, `sectors`, `tickers`, `venue` | `GET /v1/dark-pool/trades` | 5 |
| `dark_pool_top_prints` | Top-N largest prints for a ticker over a trailing window, ordered by notional | **`ticker`**, `as_of_date`, `lookback_days`, `top_n` | `GET /v1/dark-pool/top-prints/{ticker}` | 3 |

## Heatseeker — gamma/vanna heatmaps

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `heat_heatmap` | Current per-strike gamma/vanna heatmap + live velocity (multi-symbol) | **`symbols`**, `expirations`, `layout`, `max_expirations`, `max_strikes`, `metric` | `GET /v1/heatmap` | 1 |
| `heat_levels` | Key levels only: classified nodes (king, gatekeeper, pika, barney, significant), strongest first, with distance from spot | **`symbols`**, `expirations`, `max_expirations`, `max_strikes`, `metric` | `GET /v1/gex/levels` | 1 |
| `heat_historical_heatmap` | Replay the heatmap at a past instant (up to 365 days back) | **`symbols`**, **`at`**, `expirations`, `max_expirations`, `max_strikes`, `metric` | `GET /v1/historical` | 5 |
| `heat_stats_daily` | Daily gamma/vanna stats for up to 50 symbols over up to 31 days (400 symbol-days): spot OHLC, largest positive and negative strike exposure, concentration | **`symbols`**, **`from`**, `metric`, `to` | `GET /v1/stats/daily` | 5 |
| `heat_symbols` | Every symbol with gamma/vanna data: index flag, previous tickers after a rename, available metrics and history date range | none | `GET /v1/symbols` | 0 |

> **Note:** `heat_heatmap` accepts comma-separated `symbols` (e.g. `SPXW,SPY,QQQ`, the app's Trinity)
> for a single cross-asset call — handy for finding gamma/vanna walls across correlated names
> at once. For the S&P use `SPXW`: `SPX` holds only the AM-settled monthlies, with no 0DTE or
> weekly gamma (likewise `NDXP` / `NDX` and `RUTW` / `RUT`).

## Tempest — volatility suite

Tempest's precomputed volatility modules for the symbols it covers. Tempest access depends on your plan; a tool you can't use returns a clear `not_entitled` error and charges nothing.

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `tempest_iv` | Constant-maturity IV (SVX) at 1d/9d/30d/3m/6m, IV rank and percentiles, ratio to the VIX, term slope and mean-reversion odds | **`symbols`** | `GET /v1/vol/iv` | 1 |
| `tempest_term` | Implied vol per listed expiry, for contango/backwardation reads | **`symbols`** | `GET /v1/vol/term` | 1 |
| `tempest_cones` | The 1-sigma move priced from the current price to today's close, 1 day, the week, monthly opex and 30 days, as percent and price bands, with the upside and downside moves as skew prices them and the scheduled events inside each horizon (earnings, FOMC, CPI, NFP); plus fixed day, week and month ranges priced at a past close | **`symbols`** | `GET /v1/vol/cones` | 1 |
| `tempest_sigma` | Today's move in units of the one-day move priced at the prior close, move budget left, odds of 1- and 2-sigma days, last 60 sessions | **`symbols`** | `GET /v1/vol/sigma` | 1 |
| `tempest_surface` | 30-day 25-delta risk reversal and butterfly, ATM vol, skew percentile, a per-symbol SKEW index and the smile per expiry | **`symbols`** | `GET /v1/vol/surface` | 3 |
| `tempest_tilt` | One-strike-OTM call vs put imbalance (raw and forward-adjusted), the cheap side, z-score and percentile | **`symbols`** | `GET /v1/vol/tilt` | 1 |
| `tempest_events` | Next earnings date and timing, implied event move vs past realized moves, VRP and 20-day realized vol | **`symbols`** | `GET /v1/vol/events` | 1 |
| `tempest_snapshot` | Every Tempest module in one call (iv, term, cones, sigma, surface, tilt, events) | **`symbols`** | `GET /v1/vol/snapshot` | 5 |
| `tempest_market` | VIX1D/9D/VIX/3M/6M, VVIX and SKEW from SPX and VIX chains, curve state and roll, regime, Mag-7 dispersion, Fear & Greed | none | `GET /v1/vol/market` | 1 |
| `tempest_screener` | Radar: screen every covered symbol on IV rank, SVX percentiles, ratio to VIX, skew, tilt, expected move, sigma, day pace and vol repricing, earnings, VRP; up to 500 rows | `curve`, `filters`, `limit`, `offset`, `order`, `sector`, `sort` | `GET /v1/vol/screener` | 5 |
| `tempest_history` | One row per stored session at its close (OHLC, SVX per tenor, ATM vol, term slope, skew, tilt, chain depth), up to about two years | **`symbols`**, `fields`, `from`, `to` | `GET /v1/vol/history` | 1 per 10 symbol-weekdays in the window, min 1 (3 for 1 symbol x 1 month) |
| `tempest_derived` | One year daily: 20-day realized vol, VRP series and percentile, the SVX30 usual-range band, earnings-eve sessions, spot-vol correlation | **`symbols`** | `GET /v1/vol/derived` | 3 |
| `tempest_status` | When Tempest last computed, the session it belongs to, whether it is serving the frozen close, market state and coverage counts | none | `GET /v1/vol/status` | 0 |
| `tempest_symbols` | Every symbol Tempest covers, with its latest asOf and last stored daily session | none | `GET /v1/vol/symbols` | 0 |

## Account

Check your balance and limits before large pulls.

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `account_usage` | Balance in credits and US dollars, unlimited flag, and the limits that apply | none | `GET /v1/account` | 0 |

## Intelligence tools

One-call answers built from the tools above, each with a short factual `summary`, compact `data`, and `meta` (`cost`, `creditsRemaining`, `asOf`, `partial`). They are served on a separate tool list so agents that want them load only these: connect to `https://mcp.skylit.ai/mcp?toolset=intelligence`. The default `/mcp` list does not include them. See [Intelligence tools](https://www.skylit.ai/docs/mcp/intelligence).

| Tool | Returns | Arguments | Endpoint | Credits |
| --- | --- | --- | --- | --: |
| `explain_levels` | Key dealer-positioning levels for one symbol: spot, King node, flip, largest positive and negative walls, net exposure, five largest levels | **`symbol`**, `metric` | `GET /v1/gex/levels` | 1 |
| `vol_context` | 30-day implied volatility, IV rank, 1-year percentile and range, curve shape, 1-sigma expected moves by horizon (from the current price), scheduled events | **`symbol`** | `GET /v1/vol/iv` + `GET /v1/vol/cones` | 2 |
| `whats_changed` | How one symbol's board moved since an earlier instant: spot move, King node then and now, the five strikes whose net exposure changed most | **`symbol`**, **`since`**, `metric` | `GET /v1/historical` + `GET /v1/heatmap` | 6 |
| `market_brief` | VIX complex (computed from the SPX and VIX option chains), market-wide options flow (premium, call/put ratio, net premium, most active) and key levels for SPXW (S&P 500 dailies and weeklies, 0DTE included, as in the app's Trinity view) and QQQ | none | `GET /v1/gex/levels` + `GET /v1/market/overview` + `GET /v1/vol/market` | 5 |
| `flow_context` | Today's flow read for one ticker: bull/bear split and bias, sweep counts and premium, largest recent dark-pool prints | **`ticker`** | `GET /v1/chain-bull-bear/{ticker}` + `GET /v1/sweeps/{ticker}` + `GET /v1/dark-pool/top-prints/{ticker}` | 9 |
