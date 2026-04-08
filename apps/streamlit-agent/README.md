# Streamlit Agent App

This is the runnable Python starter for the workshop.

## Run

From repo root:

1. `cp .env.example .env` and set `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, and `OPENROUTER_MODEL`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `pip install -r apps/streamlit-agent/requirements.txt`
5. `python3 -m pytest apps/streamlit-agent/tests/`
6. `streamlit run apps/streamlit-agent/app.py`

## Included Example Logic

- `agent/graph.py`: 2-node LangGraph flow (`planner` -> `actor`)
- `agent/tools.py`: deterministic calculator tool
- `app.py`: Streamlit interface

## Notes

- Uses OpenRouter through an OpenAI-compatible API endpoint.
- Set `OPENROUTER_MODEL` to experiment with different model behavior.
