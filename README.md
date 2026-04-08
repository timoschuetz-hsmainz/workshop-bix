# Agentic Workshop

A starter repo for workshop participants to build agentic apps using Cursor, LangGraph, and OpenRouter.

**Got stuck? Chat with Cursor for help — that's the point!**

## What's Inside

| Path | What it provides |
|------|-----------------|
| `apps/streamlit-agent/` | Runnable Streamlit + LangGraph starter app with a planner/actor agent and a calculator tool |
| `apps/next-extension/` | Optional Next.js + shadcn extension guidance |
| `.cursor/mcp.json` | Pre-configured MCP servers (`filesystem`, `docs-langchain`, `shadcn`) |
| `AGENTS.md` | Agent roles, tool contracts, and prompting guardrails |
| `quickstarter.md` | Step-by-step setup, prerequisites, and first exercises |
| `troubleshooting.md` | Common issues and fixes |

## Tech Stack

- **UI** — Streamlit for rapid iteration
- **Agent framework** — LangChain + LangGraph
- **LLM provider** — OpenRouter (default model: `openai/gpt-4o-mini`)
- **IDE** — Cursor with MCP-assisted development

## Get Started

Follow the **[Quickstarter Guide](quickstarter.md)** — it covers prerequisites, installation, environment setup, and your first run in about 10 minutes.

## Key Links

- [Quickstarter Guide](quickstarter.md) — from zero to a working agent
- [Agent Contracts](AGENTS.md) — how the planner/actor agents and tools are designed
- [Streamlit App README](apps/streamlit-agent/README.md) — app-specific details
- [Troubleshooting](troubleshooting.md) — common issues and fixes
