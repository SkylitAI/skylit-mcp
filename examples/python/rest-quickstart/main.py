"""Skylit REST quickstart: key gamma levels + today's flow tone, with plain requests.

Read-only. It fetches market data and never places orders.

    export SKYLIT_API_KEY=...   # https://app.skylit.ai/developer
    python main.py SPY

Cost per run: account 0 + gex/levels 1 + chain-bull-bear 3 = 4 credits ($0.004).
Specs: https://api.skylit.ai/v1/openapi.json (Heatseeker, Tempest, account) and
https://www.skylit.ai/docs/flowseeker-openapi.yaml (Flowseeker).
"""

import os
import sys

import requests

BASE = "https://api.skylit.ai"


def get(session: requests.Session, path: str, **params) -> dict:
    r = session.get(f"{BASE}{path}", params=params, timeout=20)
    if not r.ok:
        # Errors are {"error": {"code": ..., "message": ...}} and are not charged.
        sys.exit(f"{r.status_code} on {path}: {r.text[:300]}")
    return r.json()


def main() -> None:
    api_key = os.environ.get("SKYLIT_API_KEY")
    if not api_key:
        sys.exit("Set SKYLIT_API_KEY (create one at https://app.skylit.ai/developer).")
    ticker = (sys.argv[1] if len(sys.argv) > 1 else "SPY").upper()

    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {api_key}"

    account = get(s, "/v1/account")  # free
    print(f"Credits before: {account['data']['creditsBalance']}")

    # Key gamma levels (Heatseeker): GET /v1/gex/levels
    levels = get(s, "/v1/gex/levels", symbols=ticker, metric="gamma")
    for sym in levels["data"]["symbols"]:
        print(f"\n{sym['symbol']}  spot {sym['spot']}  as of {sym['asOf']}")
        king = sym.get("kingNode")
        if king:
            print(f"  king node {king['strike']} ({king['distancePct']:+.2f}% from spot)")
        for lvl in sym["levels"][:8]:
            print(f"  {lvl['nodeType']:<11} {lvl['strike']:>9}  {lvl['distancePct']:+6.2f}%  value {lvl['value']:,.0f}")

    # Today's flow tone (Flowseeker): GET /v1/chain-bull-bear/{ticker}
    tone = get(s, f"/v1/chain-bull-bear/{ticker}", timeframe="1d")["data"]
    m, i = tone["metrics"], tone["interpretation"]
    print(f"\nFlow tone {tone['date']}: {i['bias']} ({i['strength']}, confidence {i['confidence']})")
    print(f"  bull {m['bullPct']:.1f}%  bear {m['bearPct']:.1f}%  neutral {m['neutralPct']:.1f}%")
    print(f"  trades {tone['tradeCount']:,}  premium ${tone['totalPremium']:,.0f}")
    print(f"  {i['description']}")


if __name__ == "__main__":
    main()
