"""Skylit market data for Python and AI agents.

    from skylit import Skylit
    client = Skylit()                      # reads SKYLIT_API_KEY
    client.gex_levels("SPY")               # key gamma levels
    client.vol("iv", "SPY,QQQ")            # Tempest implied volatility
    client.get("/v1/chain-bull-bear/SPY")  # any documented endpoint

Agents can also connect to the hosted MCP server at ``MCP_URL``.
Market data is read-only. The Nexus trading methods (``open_trade``,
``exit_trade``, ``close_futures`` and friends) place PAPER trades on your own
Nexus account and never reach a broker.
"""

from .client import API_URL, MCP_URL, TRADES_URL, Skylit, SkylitError

__all__ = ["Skylit", "SkylitError", "API_URL", "MCP_URL", "TRADES_URL"]
__version__ = "0.1.2"
