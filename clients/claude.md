# Claude (claude.ai, Claude Desktop, Claude mobile)

A custom connector added once works on claude.ai, Claude Desktop and the Claude
mobile apps. No config file or key is needed.

## Sign in with Skylit (recommended)

1. Individual plans: **Customize > Connectors > Add custom connector**.
   Team and Enterprise: an Owner adds it under **Organization settings >
   Connectors > Add > Custom > Web**, then each member clicks **Connect**.
2. Name: `Skylit`. URL: `https://mcp.skylit.ai/mcp`.
3. Click **Connect** (or **Add**, then **Connect**) and click **Approve** on the Skylit consent page.

Free plans can add one custom connector.

## API key in Claude Desktop (config file)

If you need a key instead of sign-in (for example, a shared machine), bridge to
the remote server with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote)
in `claude_desktop_config.json` (**Settings > Developer > Edit Config**), then
restart Claude Desktop. Requires Node.js.

```json
{
  "mcpServers": {
    "skylit": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.skylit.ai/mcp",
        "--header",
        "Authorization:${AUTH_HEADER}"
      ],
      "env": {
        "AUTH_HEADER": "Bearer YOUR_SKYLIT_API_KEY"
      }
    }
  }
}
```

The header is written as `Authorization:${AUTH_HEADER}` with no space after the
colon on purpose: Claude Desktop on Windows does not escape spaces inside
`args`, so the space lives inside the env value instead (per the mcp-remote README).

Sources, checked 2026-09-30:
- https://claude.com/docs/connectors/custom/add-unlisted
- https://github.com/geelen/mcp-remote
