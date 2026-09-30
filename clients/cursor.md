# Cursor

Add the server to `~/.cursor/mcp.json` (all projects) or `.cursor/mcp.json`
(one project).

## Sign in with Skylit

```json
{
  "mcpServers": {
    "skylit": { "url": "https://mcp.skylit.ai/mcp" }
  }
}
```

Open **Cursor Settings > MCP** and click **Connect** (or **Login**) next to
**skylit**, then approve on the Skylit page.

## API key

Cursor expands `${env:NAME}` in `url` and `headers`:

```json
{
  "mcpServers": {
    "skylit": {
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer ${env:SKYLIT_API_KEY}" }
    }
  }
}
```

Start Cursor from a shell where `SKYLIT_API_KEY` is exported.

Source, checked 2026-09-30: https://cursor.com/docs/context/mcp
