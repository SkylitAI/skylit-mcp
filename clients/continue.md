# Continue

Create `.continue/mcpServers/skylit.yaml` in your workspace. MCP tools are
available in Continue's agent mode.

## API key

Continue reads `${{ secrets.NAME }}` from its secret store, or from a `.env`
file in `~/.continue/`:

```yaml
name: Skylit
version: 0.0.1
schema: v1
mcpServers:
  - name: Skylit
    type: streamable-http
    url: https://mcp.skylit.ai/mcp
    requestOptions:
      headers:
        Authorization: Bearer ${{ secrets.SKYLIT_API_KEY }}
```

```bash
# ~/.continue/.env
SKYLIT_API_KEY=...
```

<!-- unverified: headers under requestOptions.headers are listed in Continue's config reference, but the Authorization example comes from a Continue GitHub issue, not the docs. -->

## Sign in with Skylit

<!-- unverified: Continue's docs do not describe MCP OAuth for workspace YAML servers. -->

Remove `requestOptions`. If your Continue version supports MCP OAuth it will
prompt you to sign in; otherwise use the API key form.

Sources, checked 2026-09-30:
- https://docs.continue.dev/customize/deep-dives/mcp
- https://docs.continue.dev/reference
