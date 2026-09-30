# ChatGPT

<!-- unverified: exact menu labels. OpenAI's developer-mode docs were checked; the help-center article with the current click path could not be fetched. -->

ChatGPT connects custom MCP servers through **developer mode** on the web, on
paid plans (Plus, Pro, Business, Enterprise, Edu). It uses sign-in (OAuth):
ChatGPT cannot send a custom API key header.

1. **Settings**: turn on **Developer mode** (under Apps & Connectors > Advanced
   settings, or Security and login, depending on your version).
2. Create a new app or connector with the URL `https://mcp.skylit.ai/mcp` and
   authentication **OAuth**.
3. ChatGPT opens the Skylit consent page. Click **Approve**.
4. In a chat, enable the Skylit connector from the tools menu and ask a question.

Sources, checked 2026-09-30:
- https://developers.openai.com/api/docs/guides/developer-mode
- https://developers.openai.com/apps-sdk/build/auth
