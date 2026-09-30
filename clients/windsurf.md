# Windsurf

<!-- unverified: config file location. The current official page (docs.windsurf.com redirects to docs.devin.ai/desktop/cascade/mcp) lists ~/.config/devin/mcp_config.json; older Windsurf builds use ~/.codeium/windsurf/mcp_config.json, confirmed by third-party guides but not the official page. -->

Open the MCP settings from the Cascade panel (or edit `mcp_config.json`) and
add the server. Depending on your version the file is
`~/.codeium/windsurf/mcp_config.json` or `~/.config/devin/mcp_config.json`
(`%APPDATA%\devin\mcp_config.json` on Windows). Opening it from the Cascade
panel always picks the right one.

Remote servers use `serverUrl`.

## Sign in with Skylit

```json
{
  "mcpServers": {
    "skylit": { "serverUrl": "https://mcp.skylit.ai/mcp" }
  }
}
```

Refresh the MCP list, then approve on the Skylit page when prompted.

## API key

Windsurf expands `${env:NAME}` in `serverUrl` and `headers`:

```json
{
  "mcpServers": {
    "skylit": {
      "serverUrl": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer ${env:SKYLIT_API_KEY}" }
    }
  }
}
```

Source, checked 2026-09-30: https://docs.windsurf.com/windsurf/cascade/mcp
(redirects to https://docs.devin.ai/desktop/cascade/mcp)
