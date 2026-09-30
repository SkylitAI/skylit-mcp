# Cline

<!-- unverified: Cline's docs do not describe OAuth for remote servers or env-var interpolation in headers. The API-key form below is the documented path. -->

Open the **MCP Servers** panel in Cline, then **Remote Servers** (name, URL,
transport), or **Configure MCP Servers** to edit `cline_mcp_settings.json`
directly. The Cline CLI reads `~/.cline/mcp.json`.

Set `"type": "streamableHttp"`. If `type` is left out, Cline assumes SSE and the
connection fails.

## API key

```json
{
  "mcpServers": {
    "skylit": {
      "type": "streamableHttp",
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer YOUR_SKYLIT_API_KEY" },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

This file holds the key in plain text. Keep it out of version control and
revoke the key on the [Developer page](https://app.skylit.ai/developer) if it
leaks.

## Sign in with Skylit

Remove `headers`. If your Cline version supports MCP OAuth it opens the Skylit
consent page; if the server shows `401 Unauthorized`, use the API key form.

Agent-readable install steps for Cline are in [`llms-install.md`](../llms-install.md).

Sources, checked 2026-09-30:
- https://docs.cline.bot/mcp/configuring-mcp-servers
- https://docs.cline.bot/mcp/connecting-to-a-remote-server
