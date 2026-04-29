# Literature Pipeline

Phase 6A adds a local scaffold for future LLM-assisted literature extraction. It does not call an LLM, call an external API, crawl the web, or modify `data/seed_rows.json`.

## Pipeline Stages

1. Discovery: collect source metadata in a local queue.
2. Extraction: draft possible obstruction-channel candidates from excerpts.
3. Human review: check theorem statements, channel labels, targets, bottlenecks, and citations.
4. Promotion: convert reviewed candidates into `ObstructionChannel` objects only under explicit trust rules.

## Trust Levels

All LLM outputs are unverified. They must use `llm_extracted_unverified` unless a human reviewer explicitly changes the trust level during promotion.

Theorem-backed status requires human verification, citation keys, evidence snippets, and reviewer notes.

## Running the Local Report

```powershell
python -m ihc_lab.cli literature-report
```

This reads:

- `data/literature_queue/raw_sources.sample.json`
- `data/literature_queue/extracted_rows.sample.json`

and writes:

- `reports/literature_queue.md`
- `reports/latex/literature_queue.tex`

## Non-Claims

LLM extraction is not theorem verification. LLM rows are not primary claims. Human review is required before theorem-backed status.
