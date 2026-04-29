"""Validation helpers for obstruction-channel datasets."""

from __future__ import annotations

from collections import Counter
from typing import Any

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import BottleneckLabel, ChannelLabel, TrustLevel


def validate_channel_record(record: ObstructionChannel) -> list[str]:
    """Return validation warnings/errors for a well-formed channel record."""

    warnings: list[str] = []

    if record.trust_level == TrustLevel.theorem_backed_literature and not record.citation_keys:
        warnings.append(f"{record.id}: theorem-backed literature row lacks citation_keys")

    if (
        record.trust_level == TrustLevel.generated_candidate
        and record.bottleneck == BottleneckLabel.none
        and record.survival_status.value != "not_applicable"
    ):
        warnings.append(f"{record.id}: generated candidate must include a bottleneck")

    if (
        ChannelLabel.cup_product_bockstein in record.channel_labels
        and record.cup_product_candidate is not None
        and not record.cup_product_candidate.is_degree_twist_valid()
    ):
        warnings.append(f"{record.id}: cup-product degree/twist check failed")

    if (
        ChannelLabel.local_discriminant in record.channel_labels
        and record.local_package is None
        and record.trust_level != TrustLevel.theorem_backed_literature
    ):
        warnings.append(f"{record.id}: local_discriminant row has no local_package")

    if record.trust_level == TrustLevel.llm_extracted_unverified:
        warnings.append(f"{record.id}: LLM-extracted row is unverified")

    return warnings


def validate_seed_rows(records: list[ObstructionChannel]) -> dict[str, Any]:
    by_channel: Counter[str] = Counter()
    by_trust_level: Counter[str] = Counter()
    by_computability_level: Counter[str] = Counter()
    warnings: list[str] = []

    for record in records:
        by_trust_level[record.trust_level.value] += 1
        by_computability_level[record.computability_level.value] += 1
        for label in record.channel_labels:
            by_channel[label.value] += 1
        warnings.extend(validate_channel_record(record))

    return {
        "total": len(records),
        "by_channel": dict(sorted(by_channel.items())),
        "by_trust_level": dict(sorted(by_trust_level.items())),
        "by_computability_level": dict(sorted(by_computability_level.items())),
        "warnings": warnings,
    }
