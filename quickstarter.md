# Quickstarter

This guide gets participants from zero to a working agent quickly.

## 1) Prerequisites

- **Python 3.10+**
- **Node.js 18+** (required for the `filesystem` MCP server)
- **Cursor**
- **An OpenRouter account and API key**

### Installing Prerequisites

**Python 3.10+**

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install python@3.12` |
| Ubuntu / Debian | `sudo apt update && sudo apt install python3 python3-venv python3-pip` |
| Windows | Download from <https://www.python.org/downloads/> and check "Add to PATH" during install |

Verify: `python3 --version`

**Node.js 18+**

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install node` |
| Any (via nvm — recommended) | `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh \| bash && nvm install 20` |
| Windows | Download the LTS installer from <https://nodejs.org/> |

Verify: `node --version`

**Cursor**

Download from <https://www.cursor.com/> and follow the installer for your OS.

**OpenRouter API Key**

It will be provided by the workshop organisers.

## 2) Setup (10-minute path)

From repo root:

1. Create `.env`:
   - `cp .env.example .env`
2. Edit `.env` and set all three values:
   - `OPENROUTER_API_KEY=...`
   - `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`
   - `OPENROUTER_MODEL=openai/gpt-4o-mini`
3. Create and activate venv:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
4. Install dependencies:
   - `pip install -r apps/streamlit-agent/requirements.txt`
5. Verify setup:
   - `cd apps/streamlit-agent && python3 -m pytest && cd ../..`
6. Launch:
   - `streamlit run apps/streamlit-agent/app.py`

Expected: Tests pass, Streamlit opens, and the assistant returns a response to your first prompt.

## 3) Environment Variables

Required in `.env`:

- `OPENROUTER_API_KEY`
- `OPENROUTER_BASE_URL` (must be `https://openrouter.ai/api/v1`)
- `OPENROUTER_MODEL` (example: `openai/gpt-4o-mini`)

## 4) What the Starter Demonstrates

The default app includes:

- A 2-node LangGraph flow (`plan` -> `act`)
- Tool calling with a deterministic local calculator tool
- Structured plan output from the planner node
- OpenRouter-backed chat model configuration

## 5) Build Fast in Cursor

Suggested development loop:

1. Ask Cursor to explain the current agent flow in `apps/streamlit-agent/agent/graph.py`.
2. Add one feature per loop (new tool, prompt tweak, better output formatting).
3. Run the Streamlit app and test with 3 prompts:
   - one knowledge question
   - one math expression
   - one edge case prompt
4. Add or update a smoke test after each meaningful change.

## 6) MCP Setup in Cursor (Implemented)

This repo includes working entries in `.cursor/mcp.json` for:

- `filesystem`: local file operations
- `docs-langchain`: official LangChain docs MCP endpoint
- `shadcn`: official shadcn MCP endpoint

If dependencies are missing for local servers (like `filesystem`), install Node.js 18+ and then restart Cursor MCP services.

Validation steps:

1. Open `.cursor/mcp.json` and confirm servers load.
2. Restart Cursor MCP services.
3. Validate each server can connect and list tools.
4. Run a simple call per server:
   - `docs-langchain`: ask a LangChain/LangGraph docs question
   - `shadcn`: list/search registry items

Recommended usage:

- `filesystem` for local file access
- `shadcn` for UI generation workflows
- `docs-langchain` for LangChain/LangGraph docs retrieval/search

## 7) MCP Health Check

Before coding, verify:

- MCP servers show as connected in Cursor
- You can run a simple tool from each configured server
- Errors are resolved before workshop coding starts

## 8) Examples to Try

1. Ask: `Calculate (12 * 8) + 5 and explain steps briefly.`
2. Ask: `Plan a short implementation for adding weather tool support.`
3. Extend toolset: add one more deterministic tool in `agent/tools.py`.

## 9) First Customizations for Participant Teams

- Swap `OPENROUTER_MODEL` and compare behavior
- Add a second tool (e.g., date helper)
- Improve planner prompt for more consistent outputs
- Add a simple guardrail in the system prompt
