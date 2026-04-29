"""Configuration for optional literature extraction LLM providers."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_PROVIDERS = {"mock", "manual", "openai-compatible", "anthropic"}


@dataclass
class LLMConfig:
    provider: str = "mock"
    model: str | None = None
    api_key_env: str | None = None
    base_url: str | None = None
    timeout_seconds: int = 60
    max_retries: int = 2
    max_tokens: int = 4096
    temperature: float = 0.0
    force_trust_level: str = "llm_extracted_unverified"
    force_review_status: str = "needs_human_review"

    def __post_init__(self) -> None:
        if self.provider not in ALLOWED_PROVIDERS:
            raise ValueError(f"unknown LLM provider: {self.provider}")
        if self.provider == "anthropic" and self.api_key_env is None:
            self.api_key_env = "ANTHROPIC_API_KEY"
        if self.provider == "openai-compatible" and self.api_key_env is None:
            self.api_key_env = "OPENAI_API_KEY"

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key_env": self.api_key_env,
            "base_url": self.base_url,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "force_trust_level": self.force_trust_level,
            "force_review_status": self.force_review_status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "LLMConfig") -> "LLMConfig":
        if isinstance(data, cls):
            return data
        extraction = data.get("extraction", {})
        base_url = data.get("base_url")
        if base_url == "":
            base_url = None
        return cls(
            provider=data.get("provider", "mock"),
            model=data.get("model"),
            api_key_env=data.get("api_key_env"),
            base_url=base_url,
            timeout_seconds=int(data.get("timeout_seconds", 60)),
            max_retries=int(data.get("max_retries", 2)),
            max_tokens=int(data.get("max_tokens", 4096)),
            temperature=float(data.get("temperature", 0.0)),
            force_trust_level=extraction.get(
                "force_trust_level",
                data.get("force_trust_level", "llm_extracted_unverified"),
            ),
            force_review_status=extraction.get(
                "force_review_status",
                data.get("force_review_status", "needs_human_review"),
            ),
        )


def load_llm_config(path: str | Path | None = None) -> LLMConfig:
    if path is None:
        return LLMConfig()
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"LLM config file not found: {config_path}")
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    return LLMConfig.from_dict(data)
