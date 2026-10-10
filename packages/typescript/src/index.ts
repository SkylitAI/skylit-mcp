/**
 * Skylit market data for TypeScript and AI agents.
 *
 *   import { Skylit } from "@skylitai/sdk";
 *   const skylit = new Skylit();          // reads SKYLIT_API_KEY
 *   await skylit.gexLevels("SPY");
 *
 * Market data is read-only. The Nexus trading methods (openTrade, exitTrade,
 * closeFutures and friends) place PAPER trades on your own Nexus account and
 * never reach a broker.
 * Agents can also connect to the hosted MCP server at MCP_URL.
 */

export const API_URL = "https://api.skylit.ai";
export const MCP_URL = "https://mcp.skylit.ai/mcp";
/** The Nexus Trades API: paper trades on your own Nexus account, same key. */
export const TRADES_URL = "https://app.skylit.ai";
export const VERSION = "0.1.3";

export type Symbols = string | readonly string[];
export type Params = Record<string, string | number | boolean | readonly string[] | undefined | null>;
/**
 * A Nexus Trades API request body, using the API's field names. Send
 * `test: true` to rehearse an order, and a `clientOrderId` you reuse on a retry
 * so the retry can't place a second order.
 */
export type TradeBody = Record<string, string | number | boolean | undefined>;
/** Every response is `{ data, meta }`; `meta` carries credits and rate-limit state. */
export interface SkylitResponse<T = unknown> {
  data: T;
  meta?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface SkylitOptions {
  /** Defaults to process.env.SKYLIT_API_KEY. Create one at https://app.skylit.ai/developer. */
  apiKey?: string;
  baseUrl?: string;
  /** Host for the Nexus trading methods (default TRADES_URL). */
  tradesUrl?: string;
  /** Request timeout in milliseconds (default 30000). */
  timeoutMs?: number;
  /** Custom fetch (tests, proxies). Defaults to the global fetch. */
  fetch?: typeof fetch;
}

/** An error answer from the API. Failed calls are not charged. */
export class SkylitError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(`${status} ${code}: ${message}`);
    this.name = "SkylitError";
  }
}

const joinSymbols = (s: Symbols): string => (typeof s === "string" ? s : s.join(","));
const seg = (s: string): string => encodeURIComponent(s);
/** Drops trailing slashes (a loop, not a regex, so a long run of slashes stays fast). */
function trimSlashes(s: string): string {
  let end = s.length;
  while (end > 0 && s[end - 1] === "/") end--;
  return s.slice(0, end);
}

export class Skylit {
  readonly baseUrl: string;
  readonly tradesUrl: string;
  readonly timeoutMs: number;
  readonly #key: string;
  readonly #fetch: typeof fetch;

  constructor(options: SkylitOptions = {}) {
    const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env;
    const key = options.apiKey ?? env?.SKYLIT_API_KEY;
    if (!key) {
      throw new Error(
        "No API key: pass { apiKey } or set SKYLIT_API_KEY (create one at https://app.skylit.ai/developer).",
      );
    }
    this.#key = key;
    this.baseUrl = trimSlashes(options.baseUrl ?? API_URL);
    this.tradesUrl = trimSlashes(options.tradesUrl ?? TRADES_URL);
    this.timeoutMs = options.timeoutMs ?? 30_000;
    this.#fetch = options.fetch ?? globalThis.fetch.bind(globalThis);
  }

  /** GET any documented endpoint, e.g. `get("/v1/gex/levels", { symbols: "SPY" })`. */
  get<T = unknown>(path: string, params: Params = {}): Promise<SkylitResponse<T>> {
    return this.#request<T>("GET", this.baseUrl, path, params);
  }

  #trading<T = unknown>(method: "GET" | "POST", path: string, params: Params = {}, payload?: TradeBody) {
    return this.#request<T>(method, this.tradesUrl, "/api/nexus/v1" + path, params, payload);
  }

  async #request<T>(
    method: "GET" | "POST",
    base: string,
    path: string,
    params: Params,
    payload?: TradeBody,
  ): Promise<SkylitResponse<T>> {
    const url = new URL(base + "/" + path.replace(/^\/+/, ""));
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null) continue;
      url.searchParams.set(k, Array.isArray(v) ? v.join(",") : String(v));
    }
    const headers: Record<string, string> = { Authorization: `Bearer ${this.#key}`, Accept: "application/json" };
    if (payload !== undefined) headers["Content-Type"] = "application/json";
    const res = await this.#fetch(url, {
      method,
      headers,
      body: payload === undefined ? undefined : JSON.stringify(payload),
      signal: AbortSignal.timeout(this.timeoutMs),
    });
    const text = await res.text();
    let body: unknown;
    try {
      body = text ? JSON.parse(text) : {};
    } catch {
      body = { error: { code: "invalid_json", message: text.slice(0, 200) } };
    }
    if (!res.ok) throw toError(res.status, res.statusText, body);
    return body as SkylitResponse<T>;
  }

  /** Balance, prices and limits for this key. Free. */
  account() {
    return this.get("/v1/account");
  }
  /** Symbols covered by the dealer-positioning endpoints. Free. */
  symbols() {
    return this.get("/v1/symbols");
  }
  /** Key gamma/vanna levels (king node, gatekeepers, flip, walls) with distance from spot. */
  gexLevels(symbols: Symbols, params: Params = {}) {
    return this.get("/v1/gex/levels", { ...params, symbols: joinSymbols(symbols) });
  }
  /** The live per-strike exposure board. */
  heatmap(symbols: Symbols, params: Params = {}) {
    return this.get("/v1/heatmap", { ...params, symbols: joinSymbols(symbols) });
  }
  /** The board as it stood at a past instant (`at` is RFC 3339). */
  historical(symbols: Symbols, at: string, params: Params = {}) {
    return this.get("/v1/historical", { ...params, symbols: joinSymbols(symbols), at });
  }
  /** Daily exposure statistics per symbol. */
  statsDaily(symbols: Symbols, params: Params = {}) {
    return this.get("/v1/stats/daily", { ...params, symbols: joinSymbols(symbols) });
  }
  /** A Tempest volatility module: iv, term, cones, sigma, tilt, events, surface, derived, snapshot, screener, history or market. */
  vol(module: string, symbols?: Symbols, params: Params = {}) {
    return this.get(`/v1/vol/${encodeURIComponent(module)}`, {
      ...params,
      symbols: symbols === undefined ? undefined : joinSymbols(symbols),
    });
  }
  /** Bull/bear pressure across a ticker's option chain. */
  flowTone(ticker: string, timeframe = "1d") {
    return this.get(`/v1/chain-bull-bear/${encodeURIComponent(ticker)}`, { timeframe });
  }

  // Nexus paper trading. Writes place PAPER trades on your own Nexus account and
  // never reach a broker. Send `test: true` to rehearse, and a `clientOrderId`
  // you reuse on a retry so the retry can't place a second order.

  /** What this key can trade in Nexus right now. Call it before any order. */
  tradingCapabilities() {
    return this.#trading("GET", "/trading/capabilities");
  }
  /** Your options and stock trades. `test: true` lists your test log. */
  trades(params: { status?: "open" | "closed" | "all"; limit?: number; offset?: number; test?: boolean } = {}) {
    return this.#trading("GET", "/trades", params);
  }
  /** One options or stock trade, with its exits. */
  trade(tradeId: string) {
    return this.#trading("GET", `/trades/${seg(tradeId)}`);
  }
  /** Open a PAPER trade: options, stocks or futures, e.g. `{ contract: "SPY 600C 10/16", quantity: 1, clientOrderId: "a1", test: true }`. */
  openTrade(order: TradeBody) {
    return this.#trading("POST", "/trades", {}, order);
  }
  /** Trim (`quantity`) or close (`closeAll: true`) an options or stock trade at market. */
  exitTrade(tradeId: string, request: TradeBody) {
    return this.#trading("POST", `/trades/${seg(tradeId)}/exits`, {}, request);
  }
  /** A futures account: balance, positions and loss rules. `account` is practice, evaluation, funded or an account id. */
  futuresAccount(account = "practice") {
    return this.#trading("GET", `/trading/accounts/${seg(account)}`);
  }
  /** Futures order and fill history, newest first. */
  futuresOrders(account = "practice", params: { limit?: number; before?: string } = {}) {
    return this.#trading("GET", `/trading/accounts/${seg(account)}/orders`, params);
  }
  /** Futures orders resting on the account. */
  futuresWorkingOrders(account = "practice") {
    return this.#trading("GET", `/trading/accounts/${seg(account)}/orders/working`);
  }
  /** One futures order. */
  futuresOrder(account: string, orderId: string) {
    return this.#trading("GET", `/trading/accounts/${seg(account)}/orders/${seg(orderId)}`);
  }
  /** Close one futures position (`ticker`) or flatten the account (`closeAll: true`). */
  closeFutures(account: string, request: TradeBody) {
    return this.#trading("POST", `/trading/accounts/${seg(account)}/close`, {}, request);
  }
  /** Cancel one resting futures order. `test: true` acts on a test order only. */
  cancelFuturesOrder(account: string, orderId: string, options: { test?: boolean } = {}) {
    return this.#trading("POST", `/trading/accounts/${seg(account)}/orders/${seg(orderId)}/cancel`, {}, { ...options });
  }
  /** Cancel every resting futures order (`cancelAll: true`) or one contract's (`ticker`). */
  cancelFuturesOrders(account: string, request: TradeBody) {
    return this.#trading("POST", `/trading/accounts/${seg(account)}/orders/cancel`, {}, request);
  }
  /** Move a resting futures order's price. Test orders can't be moved. */
  modifyFuturesOrder(account: string, orderId: string, price: number) {
    return this.#trading("POST", `/trading/accounts/${seg(account)}/orders/${seg(orderId)}/modify`, {}, { price });
  }
}

function toError(status: number, statusText: string, body: unknown): SkylitError {
  let code = "http_error";
  let message = statusText || "request failed";
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    const e = b.error;
    if (e && typeof e === "object") {
      const d = e as Record<string, unknown>;
      if (d.code) code = String(d.code);
      if (d.message) message = String(d.message);
    } else if (typeof e === "string") {
      code = e;
      if (b.error_description) message = String(b.error_description);
    }
  }
  return new SkylitError(status, code, message);
}
