# Any MCP client

| Setting | Value |
| --- | --- |
| URL | `https://mcp.skylit.ai/mcp` |
| Transport | Streamable HTTP (JSON-RPC over `POST`; responses may be `text/event-stream`) |
| Auth, option 1 | Sign in with Skylit (OAuth 2.1 with PKCE; discovery from the `401` `WWW-Authenticate` header; Client ID Metadata Documents and dynamic client registration both supported) |
| Auth, option 2 | `Authorization: Bearer <API key>` from https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=clients-generic |

The server is stateless: there is no `Mcp-Session-Id`, so every request carries
its own credential. The key must be in the `Authorization` header; `X-API-Key`
and query-string keys are not read.

## Clients that run local (stdio) servers but not remote ones

Bridge with [`mcp-remote`](https://github.com/geelen/mcp-remote) (requires Node.js).

Sign in with Skylit:

```json
{
  "mcpServers": {
    "skylit": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.skylit.ai/mcp"]
    }
  }
}
```

API key:

```json
{
  "mcpServers": {
    "skylit": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.skylit.ai/mcp", "--header", "Authorization:${AUTH_HEADER}"],
      "env": { "AUTH_HEADER": "Bearer YOUR_SKYLIT_API_KEY" }
    }
  }
}
```

## Test with MCP Inspector

```bash
# Browser UI (sign in with Skylit from the Authorization panel)
npx @modelcontextprotocol/inspector --transport http --server-url https://mcp.skylit.ai/mcp

# CLI, with a key: list the tools
npx @modelcontextprotocol/inspector --cli --transport http \
  --server-url https://mcp.skylit.ai/mcp \
  --header "Authorization: Bearer $SKYLIT_API_KEY" --method tools/list
```

## Raw HTTP

```bash
curl -sS https://mcp.skylit.ai/mcp \
  -H "Authorization: Bearer $SKYLIT_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"account_usage","arguments":{}}}'
```

`account_usage` is free. A `401` means the key or sign-in is missing, invalid or
expired; a `403` means the key is recognized but API access isn't active on the
account.

Sources, checked 2026-09-30:
- https://github.com/geelen/mcp-remote
- https://github.com/modelcontextprotocol/inspector
- https://www.skylit.ai/docs/mcp/quickstart?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=clients-generic
