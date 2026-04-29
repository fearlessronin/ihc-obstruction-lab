"""Run configured LLM clients against local extraction packets."""

from __future__ import annotations

from ihc_lab.literature.extraction_schema import ExtractedChannelCandidate
from ihc_lab.literature.llm_client import LLMClient
from ihc_lab.literature.packet_builder import ExtractionPacket
from ihc_lab.literature.parsing import parse_extracted_candidate_json
from ihc_lab.literature.prompts import LITERATURE_EXTRACTION_SYSTEM_PROMPT


def extract_candidate_from_packet(
    packet: ExtractionPacket, client: LLMClient
) -> ExtractedChannelCandidate:
    response = client.generate(
        packet.prompt,
        system=LITERATURE_EXTRACTION_SYSTEM_PROMPT,
    )
    candidate = parse_extracted_candidate_json(response)
    if candidate.source_id == "unknown":
        candidate.source_id = packet.source_id
    return candidate


def extract_candidates_from_packets(
    packets: list[ExtractionPacket], client: LLMClient
) -> list[ExtractedChannelCandidate]:
    return [extract_candidate_from_packet(packet, client) for packet in packets]
