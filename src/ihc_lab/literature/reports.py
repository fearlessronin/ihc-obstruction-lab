"""Reports for literature review queues."""

from __future__ import annotations

from collections import Counter

from ihc_lab.channels import ObstructionChannel
from ihc_lab.literature.extraction_schema import ExtractionStatus
from ihc_lab.literature.extraction_schema import ExtractedChannelCandidate
from ihc_lab.literature.packet_builder import ExtractionPacket
from ihc_lab.literature.pilot_sources import PilotLiteratureSource
from ihc_lab.literature.review_queue import ReviewQueue


def literature_queue_markdown(queue: ReviewQueue) -> str:
    counts = Counter(candidate.review_status for candidate in queue.extracted)
    lines = [
        "# Literature Queue",
        "",
        f"Sources count: {len(queue.sources)}",
        f"Extracted candidate count: {len(queue.extracted)}",
        f"Needs review count: {counts[ExtractionStatus.needs_human_review]}",
        f"Reviewed accepted count: {counts[ExtractionStatus.reviewed_accept]}",
        f"Reviewed rejected count: {counts[ExtractionStatus.reviewed_reject]}",
        f"Reviewed needs revision count: {counts[ExtractionStatus.reviewed_needs_revision]}",
        "",
        "| extraction_id | source_id | proposed channels | bottleneck | review status | missing fields |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in queue.extracted:
        lines.append(
            "| "
            f"{candidate.extraction_id} | "
            f"{candidate.source_id} | "
            f"{', '.join(candidate.proposed_channel_labels)} | "
            f"{candidate.proposed_bottleneck} | "
            f"{candidate.review_status} | "
            f"{', '.join(candidate.missing_fields)} |"
        )
    return "\n".join(lines)


def _latex_escape_text(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "^": r"\textasciicircum{}",
        "~": r"\textasciitilde{}",
    }
    escaped = text
    for source, target in replacements.items():
        escaped = escaped.replace(source, target)
    return escaped


def _soft_break(text: str) -> str:
    return _latex_escape_text(text).replace(r"\_", r"\_\allowbreak{}")


def literature_queue_latex(queue: ReviewQueue) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Literature review queue.}",
        r"\label{tab:literature-queue}",
        r"\footnotesize",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{|p{0.22\textwidth}|p{0.18\textwidth}|p{0.24\textwidth}|p{0.18\textwidth}|p{0.12\textwidth}|}",
        r"\hline",
        r"Candidate & Source & Channels & Bottleneck & Review \\",
        r"\hline",
    ]
    for candidate in queue.extracted:
        lines.append(
            f"{_soft_break(candidate.extraction_id)} & "
            f"{_soft_break(candidate.source_id)} & "
            f"{_soft_break(', '.join(candidate.proposed_channel_labels))} & "
            f"{_soft_break(candidate.proposed_bottleneck)} & "
            f"{_soft_break(candidate.review_status)} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def literature_packets_markdown(packets: list[ExtractionPacket]) -> str:
    unique_sources = {packet.source_id for packet in packets}
    lines = [
        "# Literature Extraction Packets",
        "",
        f"Packet count: {len(packets)}",
        f"Unique source count: {len(unique_sources)}",
        "",
        "| packet_id | source_id | channel hints | operation hints | bottleneck hints | matched keywords |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for packet in packets:
        lines.append(
            "| "
            f"{packet.packet_id} | "
            f"{packet.source_id} | "
            f"{', '.join(packet.channel_hints)} | "
            f"{', '.join(packet.operation_hints)} | "
            f"{', '.join(packet.bottleneck_hints)} | "
            f"{', '.join(packet.matched_keywords)} |"
        )
    return "\n".join(lines)


def llm_extraction_report_markdown(candidates: list[ExtractedChannelCandidate]) -> str:
    needs_review = [
        candidate
        for candidate in candidates
        if candidate.review_status == ExtractionStatus.needs_human_review
    ]
    unique_sources = {candidate.source_id for candidate in candidates}
    lines = [
        "# LLM Extraction Report",
        "",
        "Warning: All rows are unverified and require human review.",
        "",
        f"Extracted rows: {len(candidates)}",
        f"Needs review: {len(needs_review)}",
        f"Unique sources: {len(unique_sources)}",
        "",
        "| extraction_id | source_id | proposed channels | bottleneck | trust | review status | missing fields |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        lines.append(
            "| "
            f"{candidate.extraction_id} | "
            f"{candidate.source_id} | "
            f"{', '.join(candidate.proposed_channel_labels)} | "
            f"{candidate.proposed_bottleneck} | "
            f"{candidate.trust_level} | "
            f"{candidate.review_status} | "
            f"{', '.join(candidate.missing_fields)} |"
        )
    return "\n".join(lines)


def review_status_report_markdown(candidates: list[ExtractedChannelCandidate]) -> str:
    counts = Counter(candidate.review_status for candidate in candidates)
    lines = [
        "# Literature Review Status",
        "",
        f"Total candidates: {len(candidates)}",
        f"Needs review: {counts[ExtractionStatus.needs_human_review]}",
        f"Reviewed accept: {counts[ExtractionStatus.reviewed_accept]}",
        f"Reviewed reject: {counts[ExtractionStatus.reviewed_reject]}",
        f"Reviewed needs revision: {counts[ExtractionStatus.reviewed_needs_revision]}",
        "",
        "| extraction_id | source_id | review status | trust level | bottleneck | reviewer notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        lines.append(
            "| "
            f"{candidate.extraction_id} | "
            f"{candidate.source_id} | "
            f"{candidate.review_status} | "
            f"{candidate.trust_level} | "
            f"{candidate.proposed_bottleneck} | "
            f"{candidate.reviewer_notes or ''} |"
        )
    return "\n".join(lines)


def promoted_candidates_markdown(records: list[ObstructionChannel]) -> str:
    lines = [
        "# Promoted Literature Candidates",
        "",
        "Warning: These are exported from the review queue and are not automatically part of seed_rows.json.",
        "",
        "| id | display name | channels | trust level | bottleneck | citations |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| "
            f"{record.id} | "
            f"{record.display_name} | "
            f"{', '.join(label.value for label in record.channel_labels)} | "
            f"{record.trust_level.value} | "
            f"{record.bottleneck.value} | "
            f"{', '.join(record.citation_keys)} |"
        )
    return "\n".join(lines)


def review_status_report_latex(candidates: list[ExtractedChannelCandidate]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Literature review status.}",
        r"\label{tab:literature-review-status}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.25\textwidth}|p{0.2\textwidth}|p{0.18\textwidth}|p{0.16\textwidth}|p{0.13\textwidth}|}",
        r"\hline",
        r"Candidate & Source & Review & Trust & Bottleneck \\",
        r"\hline",
    ]
    for candidate in candidates:
        lines.append(
            f"{_soft_break(candidate.extraction_id)} & "
            f"{_soft_break(candidate.source_id)} & "
            f"{_soft_break(candidate.review_status)} & "
            f"{_soft_break(candidate.trust_level)} & "
            f"{_soft_break(candidate.proposed_bottleneck)} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def promoted_candidates_latex(records: list[ObstructionChannel]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Promoted literature candidates.}",
        r"\label{tab:promoted-literature-candidates}",
        r"\footnotesize",
        r"\begin{tabular}{|p{0.24\textwidth}|p{0.25\textwidth}|p{0.2\textwidth}|p{0.14\textwidth}|p{0.09\textwidth}|}",
        r"\hline",
        r"Record & Display & Channels & Trust & Bottleneck \\",
        r"\hline",
    ]
    for record in records:
        lines.append(
            f"{_soft_break(record.id)} & "
            f"{_soft_break(record.display_name)} & "
            f"{_soft_break(', '.join(label.value for label in record.channel_labels))} & "
            f"{_soft_break(record.trust_level.value)} & "
            f"{_soft_break(record.bottleneck.value)} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)


def pilot_sources_summary_markdown(sources: list[PilotLiteratureSource]) -> str:
    group_counts = Counter(source.pilot_group for source in sources)
    priority_counts = Counter(source.priority for source in sources)
    lines = [
        "# Pilot Literature Sources",
        "",
        "Warning: This is a curated pilot source list for atlas expansion, not a complete bibliography.",
        "",
        f"Total pilot sources: {len(sources)}",
        "",
        "## Counts by Pilot Group",
    ]
    for group, count in sorted(group_counts.items()):
        lines.append(f"- `{group}`: {count}")
    lines.extend(["", "## Counts by Priority"])
    for priority, count in sorted(priority_counts.items()):
        lines.append(f"- `{priority}`: {count}")
    lines.extend(
        [
            "",
            "| source_id | year | pilot group | intended channels | priority | bibtex key |",
            "| --- | ---: | --- | --- | ---: | --- |",
        ]
    )
    for source in sources:
        year = source.year if source.year is not None else "unknown"
        lines.append(
            "| "
            f"{source.source_id} | "
            f"{year} | "
            f"{source.pilot_group} | "
            f"{', '.join(source.intended_channel_hints)} | "
            f"{source.priority} | "
            f"{source.bibtex_key or ''} |"
        )
    return "\n".join(lines)


def pilot_source_channel_intents_markdown(sources: list[PilotLiteratureSource]) -> str:
    by_channel: dict[str, list[str]] = {}
    for source in sources:
        for channel in source.intended_channel_hints:
            by_channel.setdefault(channel, []).append(source.source_id)
    lines = [
        "# Pilot Source Channel Intents",
        "",
        "Warning: Channel intents are triage hints, not verified labels.",
        "",
        "| channel hint | source count | source ids |",
        "| --- | ---: | --- |",
    ]
    for channel, source_ids in sorted(by_channel.items()):
        lines.append(f"| {channel} | {len(source_ids)} | {', '.join(sorted(source_ids))} |")
    return "\n".join(lines)


def pilot_sources_summary_latex(sources: list[PilotLiteratureSource]) -> str:
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Pilot literature sources for atlas expansion.}",
        r"\label{tab:pilot-literature-sources}",
        r"\footnotesize",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabular}{|p{0.24\textwidth}|p{0.10\textwidth}|p{0.20\textwidth}|p{0.28\textwidth}|p{0.08\textwidth}|}",
        r"\hline",
        r"\centering\textbf{Source} & \centering\textbf{Year} & \centering\textbf{Group} & \centering\textbf{Channel hints} & \centering\arraybackslash\textbf{Priority} \\",
        r"\hline",
    ]
    for source in sources:
        year = source.year if source.year is not None else "unknown"
        lines.append(
            f"{_soft_break(source.source_id)} & "
            f"{year} & "
            f"{_soft_break(source.pilot_group)} & "
            f"{_soft_break(', '.join(source.intended_channel_hints))} & "
            f"{source.priority} \\\\"
        )
    lines.extend([r"\hline", r"\end{tabular}", r"\end{table}"])
    return "\n".join(lines)
