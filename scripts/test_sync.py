"""Checks for scripts/sync.py's offline parts. Standard library only:

    python3 -m unittest discover -s scripts -p "test_*.py"
"""

import copy
import unittest

import sync


def tool(doc, name):
    return next(t for t in doc["tools"] if t["name"] == name)


class TradingToolsMatchSpec(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec, cls.doc = sync.load_trading()

    def problems(self, mutate):
        doc = copy.deepcopy(self.doc)
        mutate(doc)
        return "\n".join(sync.check_trading(self.spec, doc))

    def test_shipped_tools_pass(self):
        self.assertEqual(sync.check_trading(self.spec, self.doc), [])

    def test_every_route_has_a_tool(self):
        def drop(doc):
            doc["tools"] = [t for t in doc["tools"] if t["name"] != "nexus_futures_close"]
            doc["count"] -= 1
        self.assertIn("no tool for POST /api/nexus/v1/trading/accounts/{account}/close", self.problems(drop))

    def test_unknown_route_and_operation_id(self):
        def bad(doc):
            tool(doc, "nexus_trade")["endpoint"] = "GET /api/nexus/v1/trades/{id}/legs"
            tool(doc, "nexus_trades")["operationId"] = "listEverything"
        out = self.problems(bad)
        self.assertIn("`nexus_trade` calls GET /api/nexus/v1/trades/{id}/legs", out)
        self.assertIn("`nexus_trades` says operationId listEverything", out)

    def test_argument_the_route_does_not_take(self):
        def bad(doc):
            tool(doc, "nexus_open_trade")["inputSchema"]["properties"]["quantitty"] = {"type": "integer"}
        self.assertIn("`nexus_open_trade` takes `quantitty`", self.problems(bad))

    def test_path_argument_must_be_required(self):
        def bad(doc):
            tool(doc, "nexus_exit_trade")["inputSchema"]["required"].remove("id")
        self.assertIn("`nexus_exit_trade` must require the path argument `id`", self.problems(bad))

    def test_write_tool_safety_rules(self):
        def bad(doc):
            t = tool(doc, "nexus_open_trade")
            t["annotations"]["readOnlyHint"] = True
            t["description"] = t["description"].replace("PAPER", "paper")
            t["inputSchema"]["required"].remove("clientOrderId")
            del t["inputSchema"]["properties"]["test"]
            t["inputSchema"]["required"].remove("test")
        out = self.problems(bad)
        self.assertIn("write tool `nexus_open_trade` must set readOnlyHint false", out)
        self.assertIn("write tool `nexus_open_trade` must say in its description that it trades PAPER", out)
        self.assertIn("write tool `nexus_open_trade` must require `clientOrderId`", out)
        self.assertIn("write tool `nexus_open_trade` must offer `test`", out)

    def test_read_tool_must_be_read_only(self):
        def bad(doc):
            tool(doc, "nexus_capabilities")["annotations"]["readOnlyHint"] = False
        self.assertIn("read tool `nexus_capabilities` must set readOnlyHint true", self.problems(bad))

    def test_no_dashes_in_copy(self):
        def bad(doc):
            tool(doc, "nexus_trade")["description"] += " " + chr(0x2014) + " fast"
        self.assertIn("`nexus_trade` copy has an em or en dash", self.problems(bad))

    def test_count_matches(self):
        def bad(doc):
            doc["count"] = 99
        self.assertIn("count is 99", self.problems(bad))


class TradesPathsAreKnown(unittest.TestCase):
    def test_trades_routes_match_the_spec(self):
        spec, _ = sync.load_trading()
        known = {sync.norm(p) for p in spec["paths"]}
        self.assertTrue(sync.path_known(sync.norm("/api/nexus/v1/trades/{id}/exits"), known))
        self.assertTrue(sync.path_known(sync.norm("/api/nexus/v1/trading/accounts/practice/orders/working"), known))
        self.assertFalse(sync.path_known(sync.norm("/api/nexus/v1/wallets"), known))
        self.assertFalse(sync.path_known(sync.norm("/v1/trades"), known))


if __name__ == "__main__":
    unittest.main()
