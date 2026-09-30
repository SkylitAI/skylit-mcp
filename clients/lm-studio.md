# LM Studio

In LM Studio, choose **Install > Edit mcp.json**.
LM Studio uses the same `mcpServers` format as Cursor.

## Sign in with Skylit

```json
{
  "mcpServers": {
    "skylit": { "url": "https://mcp.skylit.ai/mcp" }
  }
}
```

LM Studio (0.4.10 and later) runs the MCP sign-in flow. Approve on the Skylit page.

One-click install (same config):

```text
lmstudio://add_mcp?name=skylit&config=eyJ1cmwiOiJodHRwczovL21jcC5za3lsaXQuYWkvbWNwIn0%3D
```

## API key

<!-- unverified: LM Studio's docs do not say whether environment variables are expanded in headers, so this uses a literal key. -->

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

Tool calls go to Skylit's servers even when the model runs locally.

Sources, checked 2026-09-30:
- https://lmstudio.ai/docs/app/mcp
- https://lmstudio.ai/docs/app/mcp/deeplink
