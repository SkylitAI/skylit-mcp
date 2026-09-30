# Goose

## Interactive

Run `goose configure`, choose **Add Extension > Remote Extension (Streamable
HTTP)**, name it `skylit` and enter `https://mcp.skylit.ai/mcp`.

For a single session:

```bash
goose session --with-streamable-http-extension "https://mcp.skylit.ai/mcp"
```

## Config file

`~/.config/goose/config.yaml`

Sign in with Skylit (Goose opens the consent page on first use):

```yaml
extensions:
  skylit:
    name: Skylit
    type: streamable_http
    uri: https://mcp.skylit.ai/mcp
    enabled: true
    timeout: 300
```

API key, read from the environment (or Goose's secret store):

```yaml
extensions:
  skylit:
    name: Skylit
    type: streamable_http
    uri: https://mcp.skylit.ai/mcp
    enabled: true
    timeout: 300
    headers:
      Authorization: "Bearer ${SKYLIT_API_KEY}"
    env_keys:
      - SKYLIT_API_KEY
```

<!-- unverified: the docs page shows `env_keys` but not header substitution; ${VAR} expansion in `headers` was confirmed in Goose's source, not its docs. -->

## Desktop deeplink

```text
goose://extension?url=https%3A%2F%2Fmcp.skylit.ai%2Fmcp&type=streamable_http&id=skylit&name=Skylit&timeout=300
```

Source, checked 2026-09-30: https://goose-docs.ai/docs/getting-started/using-extensions/
