# Optional Next.js + shadcn Extension

Use this path when teams finish the Python starter early and want a richer frontend.

## Goal

Keep agent logic in Python initially, then add a Next.js UI that can:

- capture user prompts
- call a backend endpoint
- render structured responses

## Suggested Steps

1. Initialize Next.js app in this folder.
2. Install and initialize shadcn/ui components.
3. Create a prompt form and response card UI.
4. Connect UI to a backend endpoint (Python or Node bridge).
5. Reuse the same OpenRouter model settings for consistency.

## MCP

The `shadcn` MCP server is already configured in `.cursor/mcp.json`. Use it in Cursor to search, browse, and generate shadcn/ui components directly.

## Minimal Starter Commands

- `npx create-next-app@latest .`
- `npx shadcn@latest init`

After setup, add components:

- `npx shadcn@latest add button card textarea`
