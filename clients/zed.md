# Zed

Add a context server to your Zed `settings.json` (**Zed > Settings > Open
Settings**, or `.zed/settings.json` in a project).

## Sign in with Skylit

```json
{
  "context_servers": {
    "skylit": { "url": "https://mcp.skylit.ai/mcp" }
  }
}
```

With no `Authorization` header, Zed runs the MCP sign-in flow. Approve on the
Skylit page.

## API key

<!-- unverified: Zed's docs do not say whether environment variables are expanded in headers, so this uses a literal key. -->

```json
{
  "context_servers": {
    "skylit": {
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer YOUR_SKYLIT_API_KEY" }
    }
  }
}
```

Source, checked 2026-09-30: https://zed.dev/docs/ai/mcp
