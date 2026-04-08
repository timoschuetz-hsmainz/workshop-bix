from __future__ import annotations

import pytest

from agent.graph import build_graph, get_settings
from agent.tools import calculator


def test_calculator_tool_basic_math() -> None:
    assert calculator.invoke({"expression": "2 + 3 * 4"}) == "14"


def test_graph_compiles() -> None:
    compiled = build_graph()
    assert compiled is not None


def test_settings_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        get_settings()


def test_settings_requires_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    with pytest.raises(ValueError, match="OPENROUTER_MODEL"):
        get_settings()


def test_settings_reads_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)
    settings = get_settings()
    assert settings.api_key == "test-key"
    assert settings.model == "openai/gpt-4o-mini"
    assert settings.base_url.startswith("https://")
