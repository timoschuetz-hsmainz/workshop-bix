# Troubleshooting

## Missing OpenRouter API key

Symptom:
- App exits with a message about missing `OPENROUTER_API_KEY`.

Fix:
- Ensure `.env` exists and includes `OPENROUTER_API_KEY=...`.

## Invalid model ID

Symptom:
- Request fails with provider/model error.

Fix:
- Update `OPENROUTER_MODEL` to a valid model ID from [OpenRouter](https://openrouter.ai/).

## Rate limits or quota issues

Symptom:
- Intermittent 429 or quota errors.

Fix:
- Retry with a smaller/faster model, lower request frequency, or add credits.

## Import errors

Symptom:
- `ModuleNotFoundError` for LangChain/LangGraph/Streamlit.

Fix:
- Activate virtual environment and reinstall:
  - `pip install -r apps/streamlit-agent/requirements.txt`

## MCP server connection failures

Symptom:
- MCP tools unavailable in Cursor.

Fix:
- For remote MCPs (`docs-langchain`, `shadcn`): check internet connectivity and that the URLs in `.cursor/mcp.json` are reachable.
- For local MCPs (`filesystem`): verify Node.js 18+ is installed and `npx` is on PATH.
- Restart Cursor MCP services after any config change.
- Test each server individually before workshop use.
