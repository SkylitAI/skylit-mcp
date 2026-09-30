# Codex CLI (OpenAI)

Add the server to `~/.codex/config.toml` (or `.codex/config.toml` in a trusted
project).

## API key

```toml
[mcp_servers.skylit]
url = "https://mcp.skylit.ai/mcp"
bearer_token_env_var = "SKYLIT_API_KEY"
```

```bash
export SKYLIT_API_KEY="..."   # from https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=clients-codex-cli
codex
```

Codex sends the variable as `Authorization: Bearer <key>`. Or, in one command:

```bash
codex mcp add skylit --url https://mcp.skylit.ai/mcp --bearer-token-env-var SKYLIT_API_KEY
```

## Sign in with Skylit

Leave out `bearer_token_env_var`, then run:

```bash
codex mcp login skylit
```

**"Unauthorized" when Codex connects** means no credential reached the server.
Check that `SKYLIT_API_KEY` is exported in the shell you start Codex from.

Source, checked 2026-09-30: https://developers.openai.com/codex/mcp
