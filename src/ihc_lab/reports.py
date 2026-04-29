"""Markdown reporting helpers."""

from __future__ import annotations

from collections import Counter

from ihc_lab.channels import ObstructionChannel
from ihc_lab.datasets import dataset_summary


def channel_table_markdown(records: list[ObstructionChannel]) -> str:
    lines = [
        "| id | display name | channels | trust | obstruction status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        channels = ", ".join(label.value for label in record.channel_labels)
        lines.append(
            "| "
            f"{record.id} | {record.display_name} | {channels} | "
            f"{record.trust_level.value} | {record.obstruction_status.value} |"
        )
    return "\n".join(lines)


def bottleneck_table_markdown(records: list[ObstructionChannel]) -> str:
    counts = Counter(record.bottleneck.value for record in records)
    lines = ["| bottleneck | count |", "| --- | ---: |"]
    for label, count in sorted(counts.items()):
        lines.append(f"| {label} | {count} |")
    return "\n".join(lines)


def dataset_summary_markdown(records: list[ObstructionChannel]) -> str:
    summary = dataset_summary(records)
    lines = [f"# Dataset Summary", "", f"Total records: {summary['total']}", ""]
    lines.append("## Channels")
    for label, count in summary["by_channel"].items():
        lines.append(f"- `{label}`: {count}")
    lines.append("")
    lines.append("## Trust Levels")
    for label, count in summary["by_trust_level"].items():
        lines.append(f"- `{label}`: {count}")
    if summary["warnings"]:
        lines.append("")
        lines.append("## Warnings")
        for warning in summary["warnings"]:
            lines.append(f"- {warning}")
    return "\n".join(lines)
