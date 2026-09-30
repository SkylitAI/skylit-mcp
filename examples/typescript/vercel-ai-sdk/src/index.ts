// Research agent: Vercel AI SDK MCP client + the Skylit MCP server.
//
// Read-only. It answers questions about market data and never places orders.
//
//   export SKYLIT_API_KEY=...   # https://app.skylit.ai/developer
//   export OPENAI_API_KEY=...
//   npm start -- "What are the key gamma levels and today's flow tone for SPY?"

import { createMCPClient } from "@ai-sdk/mcp";
import { openai } from "@ai-sdk/openai";
import { generateText, isStepCount } from "ai";

const SKYLIT_MCP_URL = "https://mcp.skylit.ai/mcp";
const DEFAULT_QUESTION = "What are the key gamma levels and today's flow tone for SPY?";
const MODEL = process.env.MODEL ?? "gpt-5.4-mini";

const INSTRUCTIONS = `You are a market research assistant with read-only Skylit tools.
Keep credit use low: prefer heat_levels for gamma levels and chain_bull_bear for
the day's flow tone, and pass several symbols as one comma-separated string.
Report the numbers that answer the question and the time they are as of.
You cannot place trades. This is research, not investment advice.`;

async function main(): Promise<void> {
  const apiKey = process.env.SKYLIT_API_KEY;
  if (!apiKey) {
    console.error("Set SKYLIT_API_KEY (create one at https://app.skylit.ai/developer).");
    process.exit(1);
  }
  const question = process.argv.slice(2).join(" ") || DEFAULT_QUESTION;

  const skylit = await createMCPClient({
    transport: {
      type: "http",
      url: SKYLIT_MCP_URL,
      headers: { Authorization: `Bearer ${apiKey}` },
    },
  });

  try {
    const tools = await skylit.tools();
    const { text } = await generateText({
      model: openai(MODEL),
      instructions: INSTRUCTIONS,
      tools,
      prompt: question,
      stopWhen: isStepCount(8),
    });
    console.log(text);
  } finally {
    await skylit.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
