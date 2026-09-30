# Installing the Skylit MCP server (for AI agents)

Skylit is a hosted, remote MCP server. There is nothing to clone, build or run
locally.

- URL: `https://mcp.skylit.ai/mcp`
- Transport: streamable HTTP
- Auth: `Authorization: Bearer <API key>`. The user creates a key at
  https://app.skylit.ai/developer. Clients that support MCP OAuth can omit the
  header and let the user sign in with Skylit instead.

## Steps

1. Ask the user for their Skylit API key, or ask them to create one at
   https://app.skylit.ai/developer. Never invent, log or commit a key.
2. Add this entry to the MCP settings file (for Cline, `cline_mcp_settings.json`):

   ```json
   {
     "mcpServers": {
       "skylit": {
         "type": "streamableHttp",
         "url": "https://mcp.skylit.ai/mcp",
         "headers": { "Authorization": "Bearer USER_API_KEY" },
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

   `type` must be `streamableHttp`. Without it, Cline assumes SSE and fails to connect.
3. Verify by calling the free tool `account_usage`. It returns the credit
   balance and plan limits.
4. Try a question such as "What are the key gamma levels for SPY?" (the agent
   should call `heat_levels`).

## Troubleshooting

- `401`: the key is missing, mistyped or revoked. Check the header value starts with `Bearer `.
- `403`: the key is recognized but API access isn't active on the account.
- `402`: out of credits. The user can check the balance on the Developer page.

All tools are read-only. Tool catalog: https://www.skylit.ai/docs/mcp/tools
