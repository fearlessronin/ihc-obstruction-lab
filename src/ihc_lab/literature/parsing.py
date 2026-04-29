"""Parse and safety-normalize extracted literature candidate JSON."""

from __future__ import annotations

import json
import re
from typing import Any

from ihc_lab.literature.extraction_schema import (
    ExtractionStatus,
    ExtractedChannelCandidate,
)


RESET_NOTE = (
    "Model-supplied trust/review status was reset to "
    "unverified/needs_human_review."
)


def _json_text(text: str) -> str:
    match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _loads_json(text: str) -> Any:
    json_text = _json_text(text)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        prefix = text[:160].replace("\n", " ")
        raise ValueError(f"could not parse extracted candidate JSON near: {prefix}") from exc


def _normalize_payload(data: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(data)
    original_trust = normalized.get("trust_level")
    original_review = normalized.get("review_status")
    reset_needed = (
        original_trust not in (None, ExtractionStatus.llm_extracted_unverified)
        or original_review not in (None, ExtractionStatus.needs_human_review)
    )
    normalized["trust_level"] = ExtractionStatus.llm_extracted_unverified
    normalized["review_status"] = ExtractionStatus.needs_human_review
    snippets = list(normalized.get("evidence_snippets") or [])
    missing = list(normalized.get("missing_fields") or [])
    if not snippets and "evidence_snippets" not in missing:
        missing.append("evidence_snippets")
    normalized["evidence_snippets"] = snippets
    normalized["missing_fields"] = missing
    if reset_needed:
        notes = normalized.get("extraction_notes")
        normalized["extraction_notes"] = f"{notes} {RESET_NOTE}".strip() if notes else RESET_NOTE
    return normalized


def parse_extracted_candidate_json(text: str) -> ExtractedChannelCandidate:
    payload = _loads_json(text)
    if isinstance(payload, list):
        if len(payload) != 1:
            raise ValueError("expected one extracted candidate JSON object, found a list")
        payload = payload[0]
    if not isinstance(payload, dict):
        raise ValueError("expected extracted candidate JSON object")
    return ExtractedChannelCandidate.from_dict(_normalize_payload(payload))


def parse_many_extracted_candidates_json(text: str) -> list[ExtractedChannelCandidate]:
    payload = _loads_json(text)
    items = payload if isinstance(payload, list) else [payload]
    candidates: list[ExtractedChannelCandidate] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("expected extracted candidate JSON object")
        candidates.append(ExtractedChannelCandidate.from_dict(_normalize_payload(item)))
    return candidates
