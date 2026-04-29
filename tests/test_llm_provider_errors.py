import pytest

from ihc_lab.literature.llm_client import create_llm_client
from ihc_lab.literature.llm_config import LLMConfig


def test_anthropic_provider_missing_dependency_or_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        create_llm_client(LLMConfig(provider="anthropic", model="claude-sonnet-4-5"))


def test_openai_provider_missing_dependency_or_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        create_llm_client(LLMConfig(provider="openai-compatible", model="gpt-4o-mini"))
