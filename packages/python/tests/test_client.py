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


def test_constants_and_repr_hide_key():
    assert skylit.MCP_URL == "https://mcp.skylit.ai/mcp"
    assert "k-secret" not in repr(Skylit("k-secret"))
