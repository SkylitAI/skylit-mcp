# Claude Code

## Plugin (server + skill)

```text
/plugin marketplace add SkylitAI/skylit-mcp
/plugin install skylit@skylit
```

Then run `/mcp`, pick **skylit** and choose **Authenticate**. The plugin also
installs a short skill on how to use the tools well.

## Sign in with Skylit

```bash
claude mcp add --transport http skylit https://mcp.skylit.ai/mcp
```

Then run `/mcp`, pick **skylit** and choose **Authenticate**.

## API key (headless machines, CI)

```bash
export SKYLIT_API_KEY="..."   # from https://app.skylit.ai/developer?utm_source=github&utm_medium=developer&utm_campaign=api_distribution&utm_content=clients-claude-code
claude mcp add --transport http skylit https://mcp.skylit.ai/mcp \
  --header "Authorization: Bearer $SKYLIT_API_KEY"
```

Add `-s user` to make it available in every project, or `-s project` to write it
to the project's `.mcp.json`.

## Project `.mcp.json`

Commit this to share the server with a team. Claude Code expands `${VAR}` in
`url` and `headers`, so the key stays in each developer's environment:

```json
{
  "mcpServers": {
    "skylit": {
      "type": "http",
      "url": "https://mcp.skylit.ai/mcp",
      "headers": { "Authorization": "Bearer ${SKYLIT_API_KEY}" }
    }
  }
}
```

Leave out `headers` to use Skylit sign-in instead. Keep the header just when
`SKYLIT_API_KEY` is set for everyone who uses the file: a header with no key
in it is sent instead of the sign-in flow, and the server answers `401`.

Source, checked 2026-09-30: https://code.claude.com/docs/en/mcp
