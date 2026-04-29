"""Markdown and LaTeX reporting helpers."""

from __future__ import annotations

from collections import Counter

from ihc_lab.association_rules import (
    AssociationRule,
    filter_interesting_rules,
    mine_association_rules,
    transactions_from_feature_matrix,
)
from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import ChannelLabel
from ihc_lab.features import extract_feature_matrix
from ihc_lab.rule_classifier import classify_records


def _sorted_counts(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _cup_product_records(records: list[ObstructionChannel]) -> list[ObstructionChannel]:
    return [record for record in records if record.cup_product_candidate is not None]


def _binary_feature_names(feature_matrix: list[dict]) -> list[str]:
    return sorted(
        {
            name
            for row in feature_matrix
            for name, value in row.items()
            if isinstance(value, bool)
        }
    )


def _interesting_rules(records: list[ObstructionChannel]) -> list[AssociationRule]:
    feature_matrix = extract_feature_matrix(records)
    transactions = transactions_from_feature_matrix(feature_matrix)
    rules = mine_association_rules(transactions)
    return filter_interesting_rules(rules)


def dataset_summary_markdown(records: list[ObstructionChannel]) -> str:
    channel_counts: Counter[str] = Counter()
    for record in records:
        for label in record.channel_labels:
            channel_counts[label.value] += 1

    trust_counts = _sorted_counts([record.trust_level.value for record in records])
    obstruction_counts = _sorted_counts([record.obstruction_status.value for record in records])
    bottleneck_counts = _sorted_counts([record.bottleneck.value for record in records])

    lines = ["# Dataset Summary", "", f"Total records: {len(records)}", ""]
    lines.append("## Channels")
    for label, count in sorted(channel_counts.items()):
        lines.append(f"- `{label}`: {count}")
    lines.extend(["", "## Trust Levels"])
    for label, count in trust_counts.items():
        lines.append(f"- `{label}`: {count}")
    lines.extend(["", "## Obstruction Statuses"])
    for label, count in obstruction_counts.items():
        lines.append(f"- `{label}`: {count}")
    lines.extend(["", "## Bottlenecks"])
    for label, count in bottleneck_counts.items():
        lines.append(f"- `{label}`: {count}")
    return "\n".join(lines)


def channel_table_markdown(records: list[ObstructionChannel]) -> str:
    lines = [
        "| id | display name | channels | trust | obstruction status | bottleneck |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        channels = ", ".join(label.value for label in record.channel_labels)
        lines.append(
            "| "
            f"{record.id} | {record.display_name} | {channels} | "
            f"{record.trust_level.value} | {record.obstruction_status.value} | "
            f"{record.bottleneck.value} |"
        )
    return "\n".join(lines)


def bottleneck_table_markdown(records: list[ObstructionChannel]) -> str:
    counts = _sorted_counts([record.bottleneck.value for record in records])
    lines = ["| bottleneck | count |", "| --- | ---: |"]
    for label, count in counts.items():
        lines.append(f"| {label} | {count} |")
    return "\n".join(lines)


def _latex_source_string(degree: int, coefficient: int, twist: int) -> str:
    return rf"$H^{degree}(-,\mathbb{{Z}}/{coefficient}({twist}))$"


def _latex_target_string(degree: int, twist: int) -> str:
    return rf"$H^{degree}(-,\mathbb{{Z}}({twist}))$"


def cup_product_validation_markdown(records: list[ObstructionChannel]) -> str:
    cup_records = _cup_product_records(records)
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
    if not cup_records:
        lines.append("No cup-product Bockstein candidate rows were found.")
        return "\n".join(lines)

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
    return "\n".join(lines)


def cup_product_validation_report(records: list[ObstructionChannel]) -> str:
    """Backward-compatible alias for Phase 1 report code."""

    return cup_product_validation_markdown(records)


def classifier_report_markdown(records: list[ObstructionChannel]) -> str:
    lines = [
        "# Classifier Report",
        "",
        "| id | predicted channels | generator status | bottleneck | explanation |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in classify_records(records):
        explanations = " ".join(result.explanations)
        lines.append(
            "| "
            f"{result.record_id} | "
            f"{', '.join(result.predicted_channels)} | "
            f"{result.generator_status} | "
            f"{result.bottleneck} | "
            f"{explanations} |"
        )
    return "\n".join(lines)


def feature_matrix_markdown(records: list[ObstructionChannel]) -> str:
    feature_matrix = extract_feature_matrix(records)
    binary_features = _binary_feature_names(feature_matrix)
    selected_prefixes = (
        "channel_",
        "trust_",
        "status_",
        "bottleneck_",
        "has_",
        "local_",
        "cup_product_",
        "valid_",
    )

    lines = [
        "# Feature Matrix Summary",
        "",
        f"Total records: {len(records)}",
        f"Total binary features: {len(binary_features)}",
        "",
        "| record id | true feature count | selected true features |",
        "| --- | ---: | --- |",
    ]

    for row in feature_matrix:
        true_features = sorted(
            name for name, value in row.items() if isinstance(value, bool) and value
        )
        selected = [
            name for name in true_features if name.startswith(selected_prefixes)
        ]
        lines.append(
            "| "
            f"{row['record_id']} | "
            f"{len(true_features)} | "
            f"{', '.join(selected)} |"
        )

    return "\n".join(lines)


def association_rules_markdown(records: list[ObstructionChannel]) -> str:
    rules = _interesting_rules(records)
    lines = [
        "# Association Rules",
        "",
        "Rules mined from seed dataset.",
        "",
        "Parameters:",
        "- max antecedent size 2",
        "- min confidence 0.8",
        f"- seed records {len(records)}",
        "",
        "| antecedent | consequent | support count | support | confidence | lift |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]

    for rule in rules:
        lines.append(
            "| "
            f"{', '.join(rule.antecedent)} | "
            f"{rule.consequent} | "
            f"{rule.support_count} | "
            f"{rule.support:.2f} | "
            f"{rule.confidence:.2f} | "
            f"{rule.lift:.2f} |"
        )

    return "\n".join(lines)


def latex_escape_text(s: str) -> str:
    if "$" in s or "\\" in s:
        return s
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = s
    for source, target in replacements.items():
        escaped = escaped.replace(source, target)
    return escaped


def soft_break_identifier(s: str) -> str:
    return latex_escape_text(s).replace(r"\_", r"\_\allowbreak{}")


def _latex_count_rows(counts: dict[str, int]) -> list[str]:
    return [f"{soft_break_identifier(label)} & {count} \\\\" for label, count in counts.items()]


def seed_dataset_summary_latex(records: list[ObstructionChannel]) -> str:
    channel_counts: Counter[str] = Counter()
    for record in records:
        for label in record.channel_labels:
            channel_counts[label.value] += 1
    trust_counts = _sorted_counts([record.trust_level.value for record in records])

    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Seed dataset summary.}",
        r"\label{tab:seed-dataset-summary}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.62\textwidth}|p{0.18\textwidth}|}",
        r"\hline",
        r"Quantity & Count \\",
        r"\hline",
        f"Total records & {len(records)} \\\\",
        r"\hline",
    ]
    lines.extend(_latex_count_rows(dict(sorted(channel_counts.items()))))
    lines.append(r"\hline")
    lines.extend(_latex_count_rows(trust_counts))
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def bottleneck_summary_latex(records: list[ObstructionChannel]) -> str:
    counts = _sorted_counts([record.bottleneck.value for record in records])
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Bottleneck distribution in the seed dataset.}",
        r"\label{tab:bottleneck-summary}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.62\textwidth}|p{0.18\textwidth}|}",
        r"\hline",
        r"Bottleneck & Count \\",
        r"\hline",
    ]
    lines.extend(_latex_count_rows(counts))
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def cup_product_validation_latex(records: list[ObstructionChannel]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Cup-product Bockstein validation rows.}",
        r"\label{tab:cup-product-validation}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.24\textwidth}|p{0.08\textwidth}|p{0.08\textwidth}|p{0.16\textwidth}|p{0.08\textwidth}|p{0.22\textwidth}|}",
        r"\hline",
        r"Record & Degree & Twist & Target & Valid & Bottleneck \\",
        r"\hline",
    ]
    for record in _cup_product_records(records):
        candidate = record.cup_product_candidate
        assert candidate is not None
        valid = "yes" if candidate.is_degree_twist_valid() else "no"
        lines.append(
            f"{soft_break_identifier(record.id)} & "
            f"{candidate.total_degree()} & "
            f"{candidate.total_twist()} & "
            f"{_latex_target_string(candidate.expected_bockstein_degree(), candidate.target_codimension)} & "
            f"{valid} & "
            f"{soft_break_identifier(candidate.bottleneck.value)} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def channel_table_latex(records: list[ObstructionChannel]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Channel classification rows in the seed dataset.}",
        r"\label{tab:channel-table}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.205\textwidth}|p{0.235\textwidth}|p{0.24\textwidth}|p{0.085\textwidth}|p{0.09\textwidth}|}",
        r"\hline",
        r"Record & Display name & Channels & Trust & Status \\",
        r"\hline",
    ]
    for record in records:
        channels = ", ".join(label.value for label in record.channel_labels)
        lines.append(
            f"{soft_break_identifier(record.id)} & "
            f"{latex_escape_text(record.display_name)} & "
            f"{soft_break_identifier(channels)} & "
            f"{soft_break_identifier(record.trust_level.value)} & "
            f"{soft_break_identifier(record.obstruction_status.value)} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def classifier_report_latex(records: list[ObstructionChannel]) -> str:
    results = classify_records(records)
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Rule-based classifier output for seed rows.}",
        r"\label{tab:classifier-report}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.26\textwidth}|p{0.27\textwidth}|p{0.20\textwidth}|p{0.18\textwidth}|}",
        r"\hline",
        r"Record & Channel & Status & Bottleneck \\",
        r"\hline",
    ]
    for result in results:
        lines.append(
            f"{soft_break_identifier(result.record_id)} & "
            f"{soft_break_identifier(', '.join(result.predicted_channels))} & "
            f"{soft_break_identifier(result.generator_status)} & "
            f"{soft_break_identifier(result.bottleneck)} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}", "", r"\begin{itemize}"])
    for result in results:
        explanation = " ".join(result.explanations)
        lines.append(
            rf"\item \texttt{{{soft_break_identifier(result.record_id)}}}: "
            f"{latex_escape_text(explanation)}"
        )
    lines.append(r"\end{itemize}")
    return "\n".join(lines)


def association_rules_latex(records: list[ObstructionChannel]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Exploratory association rules mined from seed-row features.}",
        r"\label{tab:association-rules}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.38\textwidth}|p{0.28\textwidth}|p{0.12\textwidth}|p{0.14\textwidth}|}",
        r"\hline",
        r"Antecedent & Consequent & Support & Confidence \\",
        r"\hline",
    ]
    for rule in _interesting_rules(records):
        lines.append(
            f"{soft_break_identifier(', '.join(rule.antecedent))} & "
            f"{soft_break_identifier(rule.consequent)} & "
            f"{rule.support_count} & "
            f"{rule.confidence:.2f} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def feature_summary_latex(records: list[ObstructionChannel]) -> str:
    feature_matrix = extract_feature_matrix(records)
    binary_features = _binary_feature_names(feature_matrix)
    metrics = {
        "total records": len(records),
        "total binary features observed": len(binary_features),
        "multichannel rows": sum(1 for row in feature_matrix if row["is_multichannel"]),
        "rows with local package": sum(1 for row in feature_matrix if row["has_local_package"]),
        "rows with cup-product candidate": sum(
            1 for row in feature_matrix if row["has_cup_product_candidate"]
        ),
        "rows with shadow selector": sum(
            1 for row in feature_matrix if row["has_shadow_selector"]
        ),
    }

    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Feature matrix summary for the seed dataset.}",
        r"\label{tab:feature-summary}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.58\textwidth}|p{0.18\textwidth}|}",
        r"\hline",
        r"Metric & Value \\",
        r"\hline",
    ]
    for metric, value in metrics.items():
        lines.append(f"{latex_escape_text(metric)} & {value} \\\\")
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)
