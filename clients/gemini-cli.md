# Gemini CLI

## Extension (server + context file)

```bash
gemini extensions install https://github.com/SkylitAI/skylit-mcp
```

The extension adds the Skylit server with sign-in and a short `GEMINI.md`
context file. On first use, run `/mcp auth skylit` if the CLI doesn't prompt you.

## Settings file

Add the server to `~/.gemini/settings.json` (user) or `.gemini/settings.json`
(project). Use `httpUrl`: in Gemini CLI, `url` means the older SSE transport.

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

<!-- unverified: Gemini CLI's docs describe $VAR expansion for `env`; expansion in `headers` is implemented in the CLI source and used by Google's own github-mcp-server extension, but not stated in the docs. -->

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

Sources, checked 2026-09-30:
- https://geminicli.com/docs/tools/mcp-server
- https://geminicli.com/docs/extensions/reference
