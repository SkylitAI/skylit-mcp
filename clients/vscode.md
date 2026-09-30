# VS Code / GitHub Copilot

VS Code reads `.vscode/mcp.json` in a workspace, or your user configuration
(**MCP: Open User Configuration** in the Command Palette). The top-level key is
`servers`, not `mcpServers`. You can also run **MCP: Add Server** and choose
**HTTP**.

## Sign in with Skylit

```json
{
  "servers": {
    "skylit": {
      "type": "http",
      "url": "https://mcp.skylit.ai/mcp"
    }
  }
}
```

Start the server from the file or the MCP view; VS Code runs the sign-in flow.
Click **Approve** on the Skylit page.

## API key

Use an input so the key is prompted once and stored by VS Code, not written to
the file:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "skylit-api-key",
      "description": "Skylit API key (https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=clients-vscode)",
      "password": true
    }
  ],
  "servers": {
    "skylit": {
      "type": "http",
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer ${input:skylit-api-key}" }
    }
  }
}
```

Sources, checked 2026-09-30:
- https://code.visualstudio.com/docs/copilot/customization/mcp-servers
- https://code.visualstudio.com/docs/copilot/reference/mcp-configuration
