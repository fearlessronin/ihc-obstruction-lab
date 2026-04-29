from pathlib import Path

import pytest

from ihc_lab.literature.llm_config import LLMConfig, load_llm_config


def test_default_config_is_mock() -> None:
    config = load_llm_config()

    assert config.provider == "mock"
    assert config.api_key_env is None


def test_load_example_config() -> None:
    config = load_llm_config("config/llm.example.toml")

    assert config.provider == "anthropic"
    assert config.model == "claude-sonnet-4-5"
    assert config.api_key_env == "ANTHROPIC_API_KEY"
    assert config.force_trust_level == "llm_extracted_unverified"


def test_provider_default_api_key_envs() -> None:
    assert LLMConfig(provider="anthropic").api_key_env == "ANTHROPIC_API_KEY"
    assert LLMConfig(provider="openai-compatible").api_key_env == "OPENAI_API_KEY"


def test_unknown_provider_raises() -> None:
    with pytest.raises(ValueError):
        LLMConfig(provider="unknown")


def test_missing_config_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_llm_config(tmp_path / "missing.toml")
