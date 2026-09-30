# Security

## Reporting a vulnerability

Email **support@skylit.ai** with "Security" in the subject line. Include what
you found, steps to reproduce, and the affected host or file. Please do not open
a public GitHub issue for security reports, and do not include live API keys.

This repository contains documentation, client configuration and examples. It
does not contain the Skylit MCP server or API code. Reports about
`mcp.skylit.ai`, `api.skylit.ai`, `flow-api.skylit.ai`, `atlas-api.skylit.ai`
or `app.skylit.ai` are also welcome at the same address.

## If you leaked an API key

1. Revoke it on the [Developer page](https://app.skylit.ai/developer) right away.
2. Create a new key and store it in an environment variable or a secret manager.
3. Remove the key from any file, commit history or chat where it appeared.

The examples in this repository read the key from the `SKYLIT_API_KEY`
environment variable and never write it to disk.
