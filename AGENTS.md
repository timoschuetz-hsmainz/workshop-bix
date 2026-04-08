# AGENTS

This file defines the expected behavior and contracts for agents in this starter.

## Agent Roles

- **Planner**
  - Input: user goal
  - Output: concise actionable plan
  - Contract: return plain text, short and task-focused

- **Actor**
  - Input: user goal + planner output + tools
  - Output: final answer for user
  - Contract: use tools when useful, keep responses correct and concise

## Tool Contracts

- Tools must be deterministic when possible.
- Tool input/output should stay small and explicit.
- Tool failures should return actionable errors, not stack traces.

## MCP Usage

- Prefer MCP tools when they provide better context than static model memory.
- Use `docs-langchain` for LangChain/LangGraph/LangSmith questions.
- Use `shadcn` when generating or selecting UI components.
- If MCP is unavailable, state the fallback and continue with best effort.

## Prompting Guardrails

- Do not fabricate tool outputs.
- Be explicit about uncertainty.
- Prefer asking for clarification over guessing requirements.
- Keep sensitive data out of logs and responses.

## Done Criteria for Tasks

A task is done when:

1. It works in the UI.
2. A smoke test passes or is updated.
3. Docs are updated if behavior changed.
