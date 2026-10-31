"""A small, dependency-free client for the Skylit REST API (https://www.skylit.ai/docs)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable, Mapping, Optional, Union

_VERSION = "0.1.2"
API_URL = "https://api.skylit.ai"
MCP_URL = "https://mcp.skylit.ai/mcp"
# The Nexus Trades API: paper trades on your own Nexus account, same key.
TRADES_URL = "https://app.skylit.ai"

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


def _query_value(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def _seg(value: str) -> str:
    return urllib.parse.quote(str(value), safe="")


class Skylit:
    """Client for the Skylit REST API.

    ``api_key`` defaults to the ``SKYLIT_API_KEY`` environment variable
    (create one at https://app.skylit.ai/developer). Every method returns the
    parsed JSON response, ``{"data": ..., "meta": ...}``.

    Market data methods are read-only. The Nexus trading methods place PAPER
    trades on your own Nexus account (``trades_url``); nothing reaches a broker.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = API_URL,
        trades_url: str = TRADES_URL,
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
        self.trades_url = trades_url.rstrip("/")
        self.timeout = timeout

    def __repr__(self) -> str:
        return f"Skylit(base_url={self.base_url!r})"

    def get(self, path: str, params: Optional[Mapping[str, Any]] = None, **kwargs: Any) -> dict:
        """GET any documented endpoint, e.g. ``get("/v1/gex/levels", symbols="SPY")``."""
        query = {**(params or {}), **kwargs}
        if query.get("symbols") is not None:
            query["symbols"] = _symbols(query["symbols"])
        return self._request("GET", self.base_url, path, query)

    def _request(
        self,
        method: str,
        base: str,
        path: str,
        query: Optional[Mapping[str, Any]] = None,
        body: Optional[Mapping[str, Any]] = None,
    ) -> dict:
        query = {k: v for k, v in (query or {}).items() if v is not None}
        url = base + "/" + path.lstrip("/")
        if query:
            url += "?" + urllib.parse.urlencode(query)
        headers = {
            "Authorization": f"Bearer {self._key}",
            "Accept": "application/json",
            "User-Agent": f"skylit-python/{_VERSION}",
        }
        data = None
        if body is not None:
            data = json.dumps(dict(body)).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            raise _error(err) from None

    def _trading(self, method: str, path: str, query: Optional[Mapping[str, Any]] = None,
                 body: Optional[Mapping[str, Any]] = None) -> dict:
        query = {k: _query_value(v) for k, v in (query or {}).items()}
        return self._request(method, self.trades_url, "/api/nexus/v1" + path, query, body)

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

    # Nexus paper trading. Writes place PAPER trades on your own Nexus account
    # and never reach a broker. Bodies use the API's field names. Send
    # "test": True to rehearse an order, and a "clientOrderId" you reuse on a
    # retry so the retry can't place a second order.
    def trading_capabilities(self) -> dict:
        """What this key can trade in Nexus right now. Call it before any order."""
        return self._trading("GET", "/trading/capabilities")

    def trades(self, status: Optional[str] = None, *, limit: Optional[int] = None,
               offset: Optional[int] = None, test: Optional[bool] = None) -> dict:
        """Your options and stock trades (``status``: open, closed or all). ``test=True`` lists your test log."""
        return self._trading("GET", "/trades", {"status": status, "limit": limit, "offset": offset, "test": test})

    def trade(self, trade_id: str) -> dict:
        """One options or stock trade, with its exits."""
        return self._trading("GET", f"/trades/{_seg(trade_id)}")

    def open_trade(self, order: Optional[Mapping[str, Any]] = None, **fields: Any) -> dict:
        """Open a PAPER trade: options, stocks or futures, e.g.
        ``open_trade(contract="SPY 600C 10/16", quantity=1, clientOrderId="a1", test=True)``."""
        return self._trading("POST", "/trades", body={**(order or {}), **fields})

    def exit_trade(self, trade_id: str, request: Optional[Mapping[str, Any]] = None, **fields: Any) -> dict:
        """Trim (``quantity``) or close (``closeAll=True``) an options or stock trade at market."""
        return self._trading("POST", f"/trades/{_seg(trade_id)}/exits", body={**(request or {}), **fields})

    def futures_account(self, account: str = "practice") -> dict:
        """A futures account: balance, positions and loss rules. ``account`` is practice,
        evaluation, funded or an account id."""
        return self._trading("GET", f"/trading/accounts/{_seg(account)}")

    def futures_orders(self, account: str = "practice", *, limit: Optional[int] = None,
                       before: Optional[str] = None) -> dict:
        """Futures order and fill history, newest first."""
        return self._trading("GET", f"/trading/accounts/{_seg(account)}/orders", {"limit": limit, "before": before})

    def futures_working_orders(self, account: str = "practice") -> dict:
        """Futures orders resting on the account."""
        return self._trading("GET", f"/trading/accounts/{_seg(account)}/orders/working")

    def futures_order(self, account: str, order_id: str) -> dict:
        """One futures order."""
        return self._trading("GET", f"/trading/accounts/{_seg(account)}/orders/{_seg(order_id)}")

    def close_futures(self, account: str, request: Optional[Mapping[str, Any]] = None, **fields: Any) -> dict:
        """Close one futures position (``ticker``) or flatten the account (``closeAll=True``)."""
        return self._trading("POST", f"/trading/accounts/{_seg(account)}/close", body={**(request or {}), **fields})

    def cancel_futures_order(self, account: str, order_id: str, *, test: Optional[bool] = None) -> dict:
        """Cancel one resting futures order. ``test=True`` acts on a test order only."""
        body = {} if test is None else {"test": test}
        return self._trading("POST", f"/trading/accounts/{_seg(account)}/orders/{_seg(order_id)}/cancel", body=body)

    def cancel_futures_orders(self, account: str, request: Optional[Mapping[str, Any]] = None, **fields: Any) -> dict:
        """Cancel every resting futures order (``cancelAll=True``) or one contract's (``ticker``)."""
        return self._trading("POST", f"/trading/accounts/{_seg(account)}/orders/cancel", body={**(request or {}), **fields})

    def modify_futures_order(self, account: str, order_id: str, price: float) -> dict:
        """Move a resting futures order's price. Test orders can't be moved."""
        return self._trading("POST", f"/trading/accounts/{_seg(account)}/orders/{_seg(order_id)}/modify",
                             body={"price": price})


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
