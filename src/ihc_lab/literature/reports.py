"""Reports for literature review queues."""

from __future__ import annotations

from collections import Counter

from ihc_lab.literature.extraction_schema import ExtractionStatus
from ihc_lab.literature.packet_builder import ExtractionPacket
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
