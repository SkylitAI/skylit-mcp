import test from "node:test";
import assert from "node:assert/strict";
import { Skylit, SkylitError, MCP_URL } from "../dist/index.js";

function fake(status = 200, body = { data: {}, meta: {} }) {
  const seen = {};
  const fetch = async (url, init) => {
    seen.url = String(url);
    seen.auth = init.headers.Authorization;
    return new Response(JSON.stringify(body), { status });
  };
  return { seen, fetch };
}

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

test("constants; key not exposed", () => {
  assert.equal(MCP_URL, "https://mcp.skylit.ai/mcp");
  assert.ok(!JSON.stringify(new Skylit({ apiKey: "k-secret" })).includes("k-secret"));
});
