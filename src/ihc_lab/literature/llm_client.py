"""Provider adapters for optional literature extraction LLM calls."""

from __future__ import annotations

import json
import os
from typing import Protocol

from ihc_lab.literature.llm_config import LLMConfig


class LLMClient(Protocol):
    def generate(self, prompt: str, system: str | None = None) -> str:
        """Generate text from a prompt."""


class MockLLMClient:
    """Deterministic offline LLM stand-in for tests and CI."""

    def generate(self, prompt: str, system: str | None = None) -> str:
        del system
        lower_prompt = prompt.lower()
        if "fermat" in lower_prompt or "elementary divisors" in lower_prompt:
            payload = {
                "extraction_id": "mock_lattice_saturation",
                "source_id": "aljovin_movasati_villaflor_2019_fermat",
                "proposed_record_id": "mock_fermat_lattice_saturation",
                "proposed_display_name": "Mock Fermat lattice-saturation extraction",
                "proposed_channel_labels": [
                    "lattice_saturation",
                    "computed_lattice_benchmark",
                ],
                "proposed_source_packages": [
                    "linear_algebraic_cycle_lattice",
                    "hodge_cycle_lattice",
                ],
                "proposed_active_operations": [
                    "smith_normal_form",
                    "elementary_divisor_comparison",
                ],
                "proposed_survival_status": "unknown",
                "proposed_obstruction_status": "unknown",
                "proposed_computability_level": "level_2_computed_group",
                "proposed_bottleneck": "lattice_identification",
                "proposed_citation_keys": ["AljovinMovasatiVillaflor2019"],
                "evidence_snippets": ["Mock sample mentions Fermat lattice computation."],
                "missing_fields": ["full_computation_details"],
                "extraction_notes": "Offline mock extraction; not theorem verification.",
            }
        elif "unramified" in lower_prompt or "brauer" in lower_prompt:
            payload = {
                "extraction_id": "mock_unramified_channel",
                "source_id": "colliot_theleme_voisin_2012_unramified",
                "proposed_record_id": "mock_unramified_degree_four_channel",
                "proposed_display_name": "Mock unramified channel extraction",
                "proposed_channel_labels": ["brauer_unramified"],
                "proposed_source_packages": ["unramified_cohomology_class"],
                "proposed_active_operations": ["residue_test", "unramified_survival"],
                "proposed_survival_status": "unknown",
                "proposed_obstruction_status": "unknown",
                "proposed_computability_level": "level_3_theorem_import",
                "proposed_bottleneck": "verify_theorem_statement",
                "proposed_citation_keys": ["ColliotTheleneVoisin2012"],
                "evidence_snippets": ["Mock sample mentions unramified and Brauer."],
                "missing_fields": ["full_theorem_statement"],
                "extraction_notes": "Offline mock extraction; not theorem verification.",
            }
        else:
            payload = {
                "extraction_id": "mock_unknown_channel",
                "source_id": "unknown",
                "proposed_record_id": "mock_unknown_channel",
                "proposed_display_name": "Mock unknown channel extraction",
                "proposed_channel_labels": ["unknown"],
                "proposed_source_packages": ["unknown"],
                "proposed_active_operations": ["unknown"],
                "proposed_survival_status": "unknown",
                "proposed_obstruction_status": "unknown",
                "proposed_computability_level": "level_0_metadata",
                "proposed_bottleneck": "unknown",
                "proposed_citation_keys": [],
                "evidence_snippets": [],
                "missing_fields": ["evidence_snippets"],
                "extraction_notes": "Offline mock extraction; not theorem verification.",
            }
        payload["trust_level"] = "llm_extracted_unverified"
        payload["review_status"] = "needs_human_review"
        return json.dumps(payload, indent=2)


class OpenAICompatibleLLMClient:
    def __init__(
        self,
        model: str,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        timeout_seconds: int = 60,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI-compatible support requires the optional dependency 'openai'. "
                "Install it with: pip install openai"
            ) from exc
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key environment variable: {api_key_env}")
        kwargs = {"api_key": api_key, "timeout": timeout_seconds}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = OpenAI(**kwargs)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str, system: str | None = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system or ""},
                {"role": "user", "content": prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""


class AnthropicLLMClient:
    def __init__(
        self,
        model: str,
        api_key_env: str = "ANTHROPIC_API_KEY",
        base_url: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        timeout_seconds: int = 60,
    ) -> None:
        try:
            import anthropic
        except ImportError as exc:
            raise RuntimeError(
                "Anthropic support requires the optional dependency 'anthropic'. "
                "Install it with: pip install anthropic"
            ) from exc
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing Anthropic API key environment variable: {api_key_env}")
        kwargs = {"api_key": api_key, "timeout": timeout_seconds}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = anthropic.Anthropic(**kwargs)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str, system: str | None = None) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        parts: list[str] = []
        for block in message.content:
            if getattr(block, "type", None) == "text":
                parts.append(block.text)
        return "\n".join(parts)


def create_llm_client(config: LLMConfig) -> LLMClient:
    if config.provider == "mock":
        return MockLLMClient()
    if config.provider == "manual":
        raise RuntimeError("Manual import does not use LLMClient; use import-manual-extraction.")
    if config.provider == "openai-compatible":
        return OpenAICompatibleLLMClient(
            model=config.model or "gpt-4o-mini",
            api_key_env=config.api_key_env or "OPENAI_API_KEY",
            base_url=config.base_url,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout_seconds=config.timeout_seconds,
        )
    if config.provider == "anthropic":
        return AnthropicLLMClient(
            model=config.model or "claude-sonnet-4-5",
            api_key_env=config.api_key_env or "ANTHROPIC_API_KEY",
            base_url=config.base_url,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            timeout_seconds=config.timeout_seconds,
        )
    raise ValueError(f"unknown LLM provider: {config.provider}")
