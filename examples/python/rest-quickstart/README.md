# REST quickstart

No agent and no MCP: plain HTTP calls with `requests` that answer "What are the
key gamma levels and today's flow tone for SPY?"

| Call | Returns | Credits |
| --- | --- | --: |
| `GET https://api.skylit.ai/v1/account` | Balance and limits | 0 |
| `GET https://api.skylit.ai/v1/gex/levels?symbols=SPY` | Key gamma levels (king, gatekeeper and other classified nodes) with distance from spot | 1 |
| `GET https://api.skylit.ai/v1/chain-bull-bear/SPY?timeframe=1d` | The day's bull/bear split and bias for the ticker's options flow | 3 |

Read-only: it fetches data and never places orders. Order execution is left to
your own broker.

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export SKYLIT_API_KEY="..."     # https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=examples-python-rest-quickstart-readme
python main.py SPY
```

Requires Python 3.10+.

Paths and response fields were checked against the published specs:
https://api.skylit.ai/v1/openapi.json (Heatseeker, Tempest, account) and
https://www.skylit.ai/docs/flowseeker-openapi.yaml (Flowseeker; the same spec is
served with a key at https://flow-api.skylit.ai/v1/openapi.json).
`flow-api.skylit.ai` is an alias of `api.skylit.ai` for Flowseeker paths, so
either host works.
