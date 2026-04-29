"""Prompt templates for future local literature extraction workflows.

These are inert templates only. This module performs no LLM or network calls.
"""

LITERATURE_EXTRACTION_SYSTEM_PROMPT = """
You are extracting possible obstruction-channel records.
Do not verify the theorem.
Do not invent missing data.
Use "unknown" for missing fields.
Every output is llm_extracted_unverified.
Include evidence snippets.
Identify bottlenecks.
Generated output must be JSON.
""".strip()


LITERATURE_EXTRACTION_USER_TEMPLATE = """
Title: {title}
Authors: {authors}
Abstract: {abstract}
Excerpt: {excerpt}
Citation key: {citation_key}

Extract a JSON candidate with:
- proposed channel labels
- source packages
- operations
- survival/comparison tests
- obstruction target
- theorem status
- computability status
- bottleneck
- missing fields
- evidence snippets

Use "unknown" for missing fields and keep trust_level as llm_extracted_unverified.
""".strip()


HUMAN_REVIEW_PROMPT = """
Human review checklist:
- Verify theorem statement.
- Verify channel labels.
- Verify obstruction target.
- Verify bottleneck.
- Check citation key.
- Decide accept/reject/revision.
""".strip()
