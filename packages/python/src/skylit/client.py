"""A small, dependency-free client for the Skylit REST API (https://www.skylit.ai/docs)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable, Mapping, Optional, Union

_VERSION = "0.1.1"
API_URL = "https://api.skylit.ai"
MCP_URL = "https://mcp.skylit.ai/mcp"

Symbols = Union[str, Iterable[str]]


class SkylitError(Exception):
    """An error answer from the API. Failed calls are not charged."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


def _symbols(value: Symbols) -> str:
    if isinstance(value, str):
        return value
    return ",".join(value)


class Skylit:
    """Client for the Skylit REST API.

    ``api_key`` defaults to the ``SKYLIT_API_KEY`` environment variable
    (create one at https://app.skylit.ai/developer). Every method returns the
    parsed JSON response, ``{"data": ..., "meta": ...}``.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = API_URL,
        timeout: float = 30.0,
    ) -> None:
        key = api_key or os.environ.get("SKYLIT_API_KEY")
        if not key:
            raise ValueError(
                "No API key: pass api_key= or set SKYLIT_API_KEY "
                "(create one at https://app.skylit.ai/developer)."
            )
        self._key = key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def __repr__(self) -> str:
        return f"Skylit(base_url={self.base_url!r})"

    def get(self, path: str, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> dict:
        """GET any documented endpoint, e.g. ``get("/v1/gex/levels", symbols="SPY")``."""
        query = {k: v for k, v in {**(params or {}), **kwargs}.items() if v is not None}
        if "symbols" in query:
            query["symbols"] = _symbols(query["symbols"])
        url = self.base_url + "/" + path.lstrip("/")
        if query:
            url += "?" + urllib.parse.urlencode(query)
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._key}",
                "Accept": "application/json",
                "User-Agent": f"skylit-python/{_VERSION}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            raise _error(err) from None

    # Account (free)
    def account(self) -> dict:
        """Balance, prices and limits for this key. Free."""
        return self.get("/v1/account")

    def symbols(self) -> dict:
        """Symbols covered by the dealer-positioning endpoints. Free."""
        return self.get("/v1/symbols")

    # Dealer positioning (Heatseeker)
    def gex_levels(self, symbols: Symbols, **params: Any) -> dict:
        """Key gamma/vanna levels (king node, gatekeepers, flip, walls) with distance from spot."""
        return self.get("/v1/gex/levels", symbols=symbols, **params)

    def heatmap(self, symbols: Symbols, **params: Any) -> dict:
        """The live per-strike exposure board."""
        return self.get("/v1/heatmap", symbols=symbols, **params)

    def historical(self, symbols: Symbols, at: str, **params: Any) -> dict:
        """The board as it stood at a past instant (``at`` is RFC 3339)."""
        return self.get("/v1/historical", symbols=symbols, at=at, **params)

    def stats_daily(self, symbols: Symbols, **params: Any) -> dict:
        """Daily exposure statistics per symbol."""
        return self.get("/v1/stats/daily", symbols=symbols, **params)

    # Volatility (Tempest)
    def vol(self, module: str, symbols: Optional[Symbols] = None, **params: Any) -> dict:
        """A Tempest module: iv, term, cones, sigma, tilt, events, surface, derived,
        snapshot, screener, history or market."""
        return self.get(f"/v1/vol/{module}", symbols=symbols, **params)

    # Options flow (Flowseeker)
    def flow_tone(self, ticker: str, timeframe: str = "1d") -> dict:
        """Bull/bear pressure across a ticker's option chain."""
        return self.get(f"/v1/chain-bull-bear/{urllib.parse.quote(ticker, safe='')}", timeframe=timeframe)


def _error(err: urllib.error.HTTPError) -> SkylitError:
    code, message = "http_error", err.reason or "request failed"
    try:
        body = json.loads(err.read().decode("utf-8"))
        detail = body.get("error", body)
        if isinstance(detail, dict):
            code = str(detail.get("code", code))
            message = str(detail.get("message", message))
        elif isinstance(detail, str):
            code = detail
            message = str(body.get("error_description", message))
    except (ValueError, AttributeError):
        pass
    return SkylitError(err.code, code, message)
