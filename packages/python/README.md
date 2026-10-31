# skylit

A small Python client for [Skylit](https://www.skylit.ai/?utm_source=pypi&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-python-readme) market data. Skylit covers options flow, volatility, dealer positioning (GEX/vanna levels and point-in-time replay) and dark pool, and is built for AI trading agents and the people who build them.

The client has no dependencies. Market data calls are read-only. The Nexus trading calls place paper trades on your own Nexus account and never reach a broker (see below).

```bash
pip install skylit
export SKYLIT_API_KEY=...   # create one at https://app.skylit.ai/developer?utm_source=pypi&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-python-readme
```

```python
from skylit import Skylit

client = Skylit()

client.account()                              # balance, prices, limits (free)
client.gex_levels("SPY")                      # king node, gatekeepers, flip, walls
client.historical("SPY", at="2026-09-29T15:30:00Z")   # the board at a past instant
client.vol("iv", ["SPY", "QQQ"])              # Tempest implied volatility
client.vol("cones", "NVDA")                   # expected-move cones
client.flow_tone("TSLA")                      # bull/bear pressure across the chain
client.get("/v1/vol/screener", limit=20)      # any documented endpoint
```

Responses are the API's JSON, `{"data": ..., "meta": ...}`. `meta` carries the remaining credits and the rate-limit state. Errors raise `skylit.SkylitError` with `.status`, `.code` and `.message`. Failed calls are not charged.

## Nexus paper trading

The same key trades your Nexus paper accounts through the Nexus Trades API: options and stocks in your paper wallet, futures in your practice, evaluation or funded account. The server prices every fill from the live market and runs the same account rules as Nexus. Order bodies use the API's field names.

```python
client.trading_capabilities()                 # what this key can trade right now

order = client.open_trade(contract="SPY 600C 10/16", quantity=1,
                          clientOrderId="spy-call-1", test=True)   # rehearse first
client.trades("open")                         # your open options and stock trades
client.exit_trade(order["data"]["id"], quantity=1, clientOrderId="spy-call-1-trim")

client.open_trade(assetClass="futures", ticker="NQ", side="buy", quantity=1,
                  clientOrderId="nq-1", test=True)
client.futures_account("practice")            # balance, positions, loss rules
client.close_futures("practice", ticker="NQ", clientOrderId="nq-1-close", test=True)
```

- `test=True` checks and prices an order like a real one, then keeps it in your test log instead of placing it.
- Send a `clientOrderId` you make up and reuse it if you retry: you get the first order back and nothing new is placed.
- Futures resting orders: `futures_working_orders`, `futures_order`, `cancel_futures_order`, `cancel_futures_orders`, `modify_futures_order`. History: `futures_orders`.

## Agents

For Claude, ChatGPT, Cursor, Gemini CLI, LangChain, the OpenAI Agents SDK and other MCP clients, connect to the hosted MCP server at `skylit.MCP_URL` (`https://mcp.skylit.ai/mcp`). Setup guides for each client are at [SkylitAI/skylit-mcp](https://github.com/SkylitAI/skylit-mcp).

## Pricing and terms

Calls are billed in credits (1 credit = $0.001; most calls cost 1 to 5). See [the docs](https://www.skylit.ai/docs?utm_source=pypi&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-python-readme). Use of Skylit data is governed by the [API Terms](https://www.skylit.ai/api-terms?utm_source=pypi&utm_medium=developer&utm_campaign=api_distribution&utm_content=packages-python-readme), which cover personal and research use; for commercial use, contact support@skylit.ai. The MIT license covers this client's code, not Skylit data.

## Staying current

This client and [its repo](https://github.com/SkylitAI/skylit-mcp) are checked against the live API every 6 hours; new releases follow API changes.
