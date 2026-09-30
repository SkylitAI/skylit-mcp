/**
 * Skylit market data for TypeScript and AI agents.
 *
 *   import { Skylit } from "skylit";
 *   const skylit = new Skylit();          // reads SKYLIT_API_KEY
 *   await skylit.gexLevels("SPY");
 *
 * Read-only: the API serves data and never places orders.
 * Agents can also connect to the hosted MCP server at MCP_URL.
 */

export const API_URL = "https://api.skylit.ai";
export const MCP_URL = "https://mcp.skylit.ai/mcp";
export const VERSION = "0.1.0";

export type Symbols = string | readonly string[];
export type Params = Record<string, string | number | boolean | readonly string[] | undefined | null>;
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

export class Skylit {
  readonly baseUrl: string;
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
    this.baseUrl = (options.baseUrl ?? API_URL).replace(/\/+$/, "");
    this.timeoutMs = options.timeoutMs ?? 30_000;
    this.#fetch = options.fetch ?? globalThis.fetch.bind(globalThis);
  }

  /** GET any documented endpoint, e.g. `get("/v1/gex/levels", { symbols: "SPY" })`. */
  async get<T = unknown>(path: string, params: Params = {}): Promise<SkylitResponse<T>> {
    const url = new URL(this.baseUrl + "/" + path.replace(/^\/+/, ""));
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null) continue;
      url.searchParams.set(k, Array.isArray(v) ? v.join(",") : String(v));
    }
    const res = await this.#fetch(url, {
      headers: { Authorization: `Bearer ${this.#key}`, Accept: "application/json" },
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
