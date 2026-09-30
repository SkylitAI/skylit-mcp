# Raycast

<!-- unverified: Raycast's manual documents the form fields below but not whether its HTTP transport is streamable HTTP or SSE, and gives no JSON format. Not tested against the Skylit server. -->

Run **Install MCP Server** (or **Manage MCP Servers > Install New Server**) and
fill in the form.

## Sign in with Skylit

| Field | Value |
| --- | --- |
| Name | `Skylit` |
| Transport | `HTTP` |
| URL | `https://mcp.skylit.ai/mcp` |
| OAuth Type | `Dynamic` |

Save, then click **Sign In** and approve on the Skylit page.

## API key

| Field | Value |
| --- | --- |
| Transport | `HTTP` |
| URL | `https://mcp.skylit.ai/mcp` |
| HTTP Headers | `Authorization` = `Bearer YOUR_SKYLIT_API_KEY` |

Then mention `@skylit` in Raycast AI.

Source, checked 2026-09-30: https://manual.raycast.com/ai/model-context-protocol
