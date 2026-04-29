"""Markdown reporting helpers."""

from __future__ import annotations

from collections import Counter

from ihc_lab.channels import ObstructionChannel
from ihc_lab.datasets import dataset_summary
from ihc_lab.enums import ChannelLabel


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


def _latex_source_string(degree: int, coefficient: int, twist: int) -> str:
    return rf"$H^{degree}(-, \mathbb{{Z}}/{coefficient}({twist}))$"


def _latex_target_string(degree: int, twist: int) -> str:
    return rf"$H^{degree}(-, \mathbb{{Z}}({twist}))$"


def cup_product_validation_report(records: list[ObstructionChannel]) -> str:
    """Build a Markdown report for finite-coefficient cup-product candidates."""

    cup_records = [
        record
        for record in records
        if ChannelLabel.cup_product_bockstein in record.channel_labels
        and record.cup_product_candidate is not None
    ]

    lines = [
        "# Cup-Product Validation Report",
        "",
        f"Candidate rows checked: {len(cup_records)}",
        "",
        "| id | total degree | total twist | expected pre-Bockstein | target | valid | bottleneck |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]

    for record in cup_records:
        candidate = record.cup_product_candidate
        assert candidate is not None
        valid = "yes" if candidate.is_degree_twist_valid() else "no"
        lines.append(
            "| "
            f"{record.id} | "
            f"{candidate.total_degree()} | "
            f"{candidate.total_twist()} | "
            f"{candidate.expected_pre_bockstein_degree()} | "
            f"{candidate.bockstein_target_string()} | "
            f"{valid} | "
            f"{candidate.bottleneck.value} |"
        )

    lines.extend(["", "## LaTeX Summary", ""])

    for record in cup_records:
        candidate = record.cup_product_candidate
        assert candidate is not None
        source = _latex_source_string(
            candidate.total_degree(),
            candidate.coefficient,
            candidate.target_codimension,
        )
        target = _latex_target_string(
            candidate.expected_bockstein_degree(),
            candidate.target_codimension,
        )
        status = "valid" if candidate.is_degree_twist_valid() else "invalid"
        lines.append(f"- `{record.id}`: {source} $\\xrightarrow{{\\beta}}$ {target} ({status}).")

    if not cup_records:
        lines.append("No cup-product Bockstein candidate rows were found.")

    return "\n".join(lines)
