# Gemini CLI

## Extension (server + context file)

```bash
gemini extensions install https://github.com/SkylitAI/skylit-mcp
```

The extension adds the Skylit server with sign-in and a short `GEMINI.md`
context file. On first use, run `/mcp auth skylit` if the CLI doesn't prompt you.

## Settings file

Add the server to `~/.gemini/settings.json` (user) or `.gemini/settings.json`
(project). Use `httpUrl`: it picks the streamable HTTP transport in every
Gemini CLI version, while older versions read a plain `url` as the SSE transport.

Sign in with Skylit:

```json
{
  "mcpServers": {
    "skylit": { "httpUrl": "https://mcp.skylit.ai/mcp" }
  }
}
```

Gemini CLI detects the `401`, discovers the sign-in endpoints and opens the
Skylit consent page. You can also run `/mcp auth skylit`.

API key:

Gemini CLI fills in `$VAR` and `${VAR}` from your environment across the whole
settings file, `headers` included, so the key stays out of the file.

```json
{
  "mcpServers": {
    "skylit": {
      "httpUrl": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer $SKYLIT_API_KEY" }
    }
  }
}
```

## CLI

```bash
gemini mcp add --transport http -s user skylit https://mcp.skylit.ai/mcp
# or, with a key:
gemini mcp add --transport http -s user \
  -H "Authorization: Bearer $SKYLIT_API_KEY" skylit https://mcp.skylit.ai/mcp
```

Sources, checked 2026-10-24 against Gemini CLI v0.65.0:
- https://geminicli.com/docs/tools/mcp-server
- https://geminicli.com/docs/extensions/reference
- https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/cli/src/config/settings.ts (environment expansion)
- https://github.com/google-gemini/gemini-cli/blob/v0.65.0/packages/core/src/tools/mcp-client.ts (transport choice)
