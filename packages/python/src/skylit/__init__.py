"""Skylit market data for Python and AI agents.

    from skylit import Skylit
    client = Skylit()                      # reads SKYLIT_API_KEY
    client.gex_levels("SPY")               # key gamma levels
    client.vol("iv", "SPY,QQQ")            # Tempest implied volatility
    client.get("/v1/chain-bull-bear/SPY")  # any documented endpoint

Agents can also connect to the hosted MCP server at ``MCP_URL``.
Read-only: the API serves data and never places orders.
"""

from .client import API_URL, MCP_URL, Skylit, SkylitError

__all__ = ["Skylit", "SkylitError", "API_URL", "MCP_URL"]
__version__ = "0.1.0"
