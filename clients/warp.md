# Warp

Add the server in **Settings > Agents > MCP servers**, or edit
`~/.warp/.mcp.json` (all projects) or `.warp/.mcp.json` (one project). Warp also
picks up servers already defined for Claude Code (`.mcp.json`) and Codex.

## Sign in with Skylit

```json
{
  "mcpServers": {
    "skylit": { "url": "https://mcp.skylit.ai/mcp" }
  }
}
```

Warp opens the Skylit consent page in your browser and stores the credential on
your device. Warp's cloud agents don't support OAuth; use a key there.

## API key

<!-- unverified: Warp's docs do not say whether environment variables are expanded in headers, so this uses a literal key. -->

```json
{
  "mcpServers": {
    "skylit": {
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer YOUR_SKYLIT_API_KEY" }
    }
  }
}
```

Source, checked 2026-09-30: https://docs.warp.dev/knowledge-and-collaboration/mcp
