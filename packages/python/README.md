# skylit

A small Python client for [Skylit](https://www.skylit.ai) market data. Skylit covers options flow, volatility, dealer positioning (GEX/vanna levels and point-in-time replay) and dark pool, and is built for AI trading agents and the people who build them.

The client has no dependencies, and every call is read-only: it fetches data and never places orders.

```bash
pip install skylit
export SKYLIT_API_KEY=...   # create one at https://app.skylit.ai/developer
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

## Agents

For Claude, ChatGPT, Cursor, Gemini CLI, LangChain, the OpenAI Agents SDK and other MCP clients, connect to the hosted MCP server at `skylit.MCP_URL` (`https://mcp.skylit.ai/mcp`). Setup guides for each client are at [SkylitAI/skylit-mcp](https://github.com/SkylitAI/skylit-mcp).

## Pricing and terms

Calls are billed in credits (1 credit = $0.001; most calls cost 1 to 5). See [the docs](https://www.skylit.ai/docs). Use of Skylit data is governed by the [API Terms](https://www.skylit.ai/api-terms), which cover personal and research use; for commercial use, contact support@skylit.ai. The MIT license covers this client's code, not Skylit data.
