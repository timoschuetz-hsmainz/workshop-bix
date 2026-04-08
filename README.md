# Agentic Workshop Quickstarter

This repo is a fast starter for participants to build agentic apps with a Python-first path:

- `Streamlit` UI for rapid iteration
- `LangChain` + `LangGraph` for agent logic
- `OpenRouter` as the default LLM provider
- `Cursor` + MCP setup for assisted development

**Got stuck? You can always chat with Cursor for help!**

## Quick Start

1. Copy the example and configure env file:
   - `cp .env.example .env`
   - Edit `.env` and set `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`
2. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
3. Install dependencies:
   - `pip install -r apps/streamlit-agent/requirements.txt`
4. Verify setup:
   - `python3 -m pytest apps/streamlit-agent/tests/`
5. Run the app:
   - `streamlit run apps/streamlit-agent/app.py`

For the full setup path and learning flow, see:

- [quickstarter.md](quickstarter.md)
- [AGENTS.md](AGENTS.md)
- [apps/streamlit-agent/README.md](apps/streamlit-agent/README.md)

## Repository Map

- `quickstarter.md`: step-by-step onboarding and examples
- `AGENTS.md`: agent roles, contracts, and guardrails
- `.cursor/mcp.json`: repo-level MCP template for Cursor
- `apps/streamlit-agent/`: runnable starter app
- `apps/next-extension/`: optional Next.js + shadcn extension guidance

## OpenRouter-First Defaults

This repo expects:

- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`
- `OPENROUTER_MODEL=<model-id>`
