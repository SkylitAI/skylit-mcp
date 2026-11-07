import test from "node:test";
import assert from "node:assert/strict";
import { Skylit, SkylitError, MCP_URL, TRADES_URL } from "../dist/index.js";

function fake(status = 200, body = { data: {}, meta: {} }) {
  const seen = {};
  const fetch = async (url, init) => {
    seen.url = String(url);
    seen.auth = init.headers.Authorization;
    seen.method = init.method;
    seen.type = init.headers["Content-Type"];
    seen.body = init.body === undefined ? undefined : JSON.parse(init.body);
    return new Response(JSON.stringify(body), { status });
  };
  return { seen, fetch };
}

const T = "https://app.skylit.ai/api/nexus/v1";

test("bearer header and account path", async () => {
  const { seen, fetch } = fake();
  await new Skylit({ apiKey: "k1", fetch }).account();
  assert.equal(seen.url, "https://api.skylit.ai/v1/account");
  assert.equal(seen.auth, "Bearer k1");
});

test("key from env; missing key is a clear error", () => {
  const prev = process.env.SKYLIT_API_KEY;
  delete process.env.SKYLIT_API_KEY;
  assert.throws(() => new Skylit(), /SKYLIT_API_KEY/);
  process.env.SKYLIT_API_KEY = "envkey";
  assert.ok(new Skylit());
  if (prev === undefined) delete process.env.SKYLIT_API_KEY; else process.env.SKYLIT_API_KEY = prev;
});

test("symbol lists joined, nulls dropped", async () => {
  const { seen, fetch } = fake();
  await new Skylit({ apiKey: "k", fetch }).gexLevels(["SPY", "QQQ"], { metric: "gamma", foo: undefined });
  assert.equal(seen.url, "https://api.skylit.ai/v1/gex/levels?metric=gamma&symbols=SPY%2CQQQ");
});

test("vol and flow paths", async () => {
  const { seen, fetch } = fake();
  const c = new Skylit({ apiKey: "k", fetch });
  await c.vol("market");
  assert.equal(seen.url, "https://api.skylit.ai/v1/vol/market");
  await c.flowTone("SPY");
  assert.equal(seen.url, "https://api.skylit.ai/v1/chain-bull-bear/SPY?timeframe=1d");
});

test("error bodies parsed (both shapes)", async () => {
  let { fetch } = fake(402, { error: { code: "insufficient_credits", message: "Add funds" } });
  await assert.rejects(new Skylit({ apiKey: "k", fetch }).account(), (e) =>
    e instanceof SkylitError && e.status === 402 && e.code === "insufficient_credits" && e.message.includes("Add funds"));
  ({ fetch } = fake(401, { error: "unauthorized", error_description: "bad key" }));
  await assert.rejects(new Skylit({ apiKey: "k", fetch }).account(), (e) => e.code === "unauthorized");
});

test("trading reads go to the trades host", async () => {
  const { seen, fetch } = fake();
  const c = new Skylit({ apiKey: "k", fetch });
  await c.tradingCapabilities();
  assert.deepEqual([seen.method, seen.url, seen.auth, seen.body], ["GET", `${T}/trading/capabilities`, "Bearer k", undefined]);
  await c.trades({ status: "open", limit: 10, test: true });
  assert.equal(seen.url, `${T}/trades?status=open&limit=10&test=true`);
  await c.trade("t-1");
  assert.equal(seen.url, `${T}/trades/t-1`);
  await c.futuresAccount();
  assert.equal(seen.url, `${T}/trading/accounts/practice`);
  await c.futuresOrders("evaluation", { limit: 5, before: "2026-10-09T14:00:00Z" });
  assert.equal(seen.url, `${T}/trading/accounts/evaluation/orders?limit=5&before=2026-10-09T14%3A00%3A00Z`);
  await c.futuresWorkingOrders("funded");
  assert.equal(seen.url, `${T}/trading/accounts/funded/orders/working`);
  await c.futuresOrder("practice", "o/1");
  assert.equal(seen.url, `${T}/trading/accounts/practice/orders/o%2F1`);
});

test("trading writes post JSON bodies", async () => {
  const { seen, fetch } = fake();
  const c = new Skylit({ apiKey: "k", fetch });
  await c.openTrade({ contract: "SPY 600C 10/16", quantity: 1, clientOrderId: "a1", test: true });
  assert.deepEqual([seen.method, seen.url, seen.type], ["POST", `${T}/trades`, "application/json"]);
  assert.deepEqual(seen.body, { contract: "SPY 600C 10/16", quantity: 1, clientOrderId: "a1", test: true });
  await c.exitTrade("t1", { quantity: 1, clientOrderId: "x1" });
  assert.deepEqual([seen.url, seen.body], [`${T}/trades/t1/exits`, { quantity: 1, clientOrderId: "x1" }]);
  await c.closeFutures("practice", { closeAll: true, clientOrderId: "c1", test: true });
  assert.deepEqual([seen.url, seen.body], [`${T}/trading/accounts/practice/close`, { closeAll: true, clientOrderId: "c1", test: true }]);
  await c.cancelFuturesOrder("practice", "o1");
  assert.deepEqual([seen.url, seen.body], [`${T}/trading/accounts/practice/orders/o1/cancel`, {}]);
  await c.cancelFuturesOrder("practice", "o1", { test: true });
  assert.deepEqual(seen.body, { test: true });
  await c.cancelFuturesOrders("practice", { ticker: "NQ" });
  assert.deepEqual([seen.url, seen.body], [`${T}/trading/accounts/practice/orders/cancel`, { ticker: "NQ" }]);
  await c.modifyFuturesOrder("practice", "o1", 25295);
  assert.deepEqual([seen.method, seen.url, seen.body], ["POST", `${T}/trading/accounts/practice/orders/o1/modify`, { price: 25295 }]);
});

test("trading refusals throw SkylitError; trades host configurable", async () => {
  let { fetch } = fake(422, { error: { code: "price_outside_market", message: "outside the window" } });
  await assert.rejects(
    new Skylit({ apiKey: "k", fetch }).openTrade({ contract: "SPY 600C 10/16 @ 9.99", quantity: 1, clientOrderId: "a2", test: true }),
    (e) => e instanceof SkylitError && e.status === 422 && e.code === "price_outside_market");
  const f = fake();
  await new Skylit({ apiKey: "k", fetch: f.fetch, tradesUrl: "http://localhost:9///" }).tradingCapabilities();
  assert.equal(f.seen.url, "http://localhost:9/api/nexus/v1/trading/capabilities");
});

test("constants; key not exposed", () => {
  assert.equal(MCP_URL, "https://mcp.skylit.ai/mcp");
  assert.equal(TRADES_URL, "https://app.skylit.ai");
  assert.ok(!JSON.stringify(new Skylit({ apiKey: "k-secret" })).includes("k-secret"));
});
