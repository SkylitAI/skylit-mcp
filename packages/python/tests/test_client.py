import io
import json
import urllib.error
import urllib.request

import pytest

import skylit
from skylit import Skylit, SkylitError


class _Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _capture(monkeypatch, payload=None, error=None):
    seen = {}

    def fake_urlopen(req, timeout):
        seen["url"] = req.full_url
        seen["auth"] = req.get_header("Authorization")
        seen["timeout"] = timeout
        seen["method"] = req.get_method()
        seen["type"] = req.get_header("Content-type")
        seen["body"] = json.loads(req.data) if req.data else None
        if error:
            raise error
        return _Resp(json.dumps(payload or {"data": {}, "meta": {}}).encode())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    return seen


def test_key_from_env_and_bearer_header(monkeypatch):
    monkeypatch.setenv("SKYLIT_API_KEY", "k123")
    seen = _capture(monkeypatch)
    Skylit().account()
    assert seen["url"] == "https://api.skylit.ai/v1/account"
    assert seen["auth"] == "Bearer k123"


def test_missing_key_is_a_clear_error(monkeypatch):
    monkeypatch.delenv("SKYLIT_API_KEY", raising=False)
    with pytest.raises(ValueError, match="SKYLIT_API_KEY"):
        Skylit()


def test_symbol_lists_are_joined_and_none_params_dropped(monkeypatch):
    seen = _capture(monkeypatch)
    Skylit("k").gex_levels(["SPY", "QQQ"], metric="gamma", foo=None)
    assert seen["url"] == "https://api.skylit.ai/v1/gex/levels?symbols=SPY%2CQQQ&metric=gamma"


def test_vol_and_flow_paths(monkeypatch):
    seen = _capture(monkeypatch)
    c = Skylit("k")
    c.vol("iv", "SPY")
    assert seen["url"] == "https://api.skylit.ai/v1/vol/iv?symbols=SPY"
    c.vol("market")
    assert seen["url"] == "https://api.skylit.ai/v1/vol/market"
    c.flow_tone("SPY")
    assert seen["url"] == "https://api.skylit.ai/v1/chain-bull-bear/SPY?timeframe=1d"


def test_error_body_is_parsed(monkeypatch):
    body = io.BytesIO(json.dumps({"error": {"code": "insufficient_credits", "message": "Add funds"}}).encode())
    err = urllib.error.HTTPError("u", 402, "Payment Required", {}, body)
    _capture(monkeypatch, error=err)
    with pytest.raises(SkylitError) as e:
        Skylit("k").account()
    assert (e.value.status, e.value.code, e.value.message) == (402, "insufficient_credits", "Add funds")


def test_oauth_style_error_body(monkeypatch):
    body = io.BytesIO(json.dumps({"error": "unauthorized", "error_description": "bad key"}).encode())
    err = urllib.error.HTTPError("u", 401, "Unauthorized", {}, body)
    _capture(monkeypatch, error=err)
    with pytest.raises(SkylitError) as e:
        Skylit("k").account()
    assert (e.value.code, e.value.message) == ("unauthorized", "bad key")


T = "https://app.skylit.ai/api/nexus/v1"


def test_trading_reads_go_to_the_trades_host(monkeypatch):
    seen = _capture(monkeypatch)
    c = Skylit("k")
    c.trading_capabilities()
    assert (seen["method"], seen["url"], seen["auth"]) == ("GET", f"{T}/trading/capabilities", "Bearer k")
    c.trades("open", limit=10, test=True)
    assert seen["url"] == f"{T}/trades?status=open&limit=10&test=true"
    c.trades()
    assert seen["url"] == f"{T}/trades"
    c.trade("t-1")
    assert seen["url"] == f"{T}/trades/t-1"
    c.futures_account()
    assert seen["url"] == f"{T}/trading/accounts/practice"
    c.futures_orders("evaluation", limit=5, before="2026-10-09T14:00:00Z")
    assert seen["url"] == f"{T}/trading/accounts/evaluation/orders?limit=5&before=2026-10-09T14%3A00%3A00Z"
    c.futures_working_orders("funded")
    assert seen["url"] == f"{T}/trading/accounts/funded/orders/working"
    c.futures_order("practice", "o/1")
    assert seen["url"] == f"{T}/trading/accounts/practice/orders/o%2F1"
    assert seen["body"] is None


def test_open_trade_posts_the_order_as_json(monkeypatch):
    seen = _capture(monkeypatch)
    Skylit("k").open_trade({"contract": "SPY 600C 10/16", "quantity": 1}, clientOrderId="a1", test=True)
    assert (seen["method"], seen["url"], seen["type"]) == ("POST", f"{T}/trades", "application/json")
    assert seen["body"] == {"contract": "SPY 600C 10/16", "quantity": 1, "clientOrderId": "a1", "test": True}


def test_trading_writes(monkeypatch):
    seen = _capture(monkeypatch)
    c = Skylit("k")
    c.exit_trade("t1", quantity=1, clientOrderId="x1")
    assert (seen["method"], seen["url"], seen["body"]) == ("POST", f"{T}/trades/t1/exits", {"quantity": 1, "clientOrderId": "x1"})
    c.close_futures("practice", closeAll=True, clientOrderId="c1", test=True)
    assert (seen["url"], seen["body"]) == (f"{T}/trading/accounts/practice/close", {"closeAll": True, "clientOrderId": "c1", "test": True})
    c.cancel_futures_order("practice", "o1")
    assert (seen["url"], seen["body"]) == (f"{T}/trading/accounts/practice/orders/o1/cancel", {})
    c.cancel_futures_order("practice", "o1", test=True)
    assert seen["body"] == {"test": True}
    c.cancel_futures_orders("practice", {"ticker": "NQ"})
    assert (seen["url"], seen["body"]) == (f"{T}/trading/accounts/practice/orders/cancel", {"ticker": "NQ"})
    c.modify_futures_order("practice", "o1", 25295)
    assert (seen["url"], seen["body"]) == (f"{T}/trading/accounts/practice/orders/o1/modify", {"price": 25295})
    assert seen["method"] == "POST"


def test_trading_refusal_is_a_skylit_error(monkeypatch):
    body = io.BytesIO(json.dumps({"error": {"code": "price_outside_market", "message": "outside the window"}}).encode())
    _capture(monkeypatch, error=urllib.error.HTTPError("u", 422, "Unprocessable", {}, body))
    with pytest.raises(SkylitError) as e:
        Skylit("k").open_trade(contract="SPY 600C 10/16 @ 9.99", quantity=1, clientOrderId="a2", test=True)
    assert (e.value.status, e.value.code) == (422, "price_outside_market")


def test_trades_url_is_configurable(monkeypatch):
    seen = _capture(monkeypatch)
    Skylit("k", trades_url="http://localhost:9/").trading_capabilities()
    assert seen["url"] == "http://localhost:9/api/nexus/v1/trading/capabilities"


def test_constants_and_repr_hide_key():
    assert skylit.TRADES_URL == "https://app.skylit.ai"
    assert skylit.MCP_URL == "https://mcp.skylit.ai/mcp"
    assert "k-secret" not in repr(Skylit("k-secret"))
