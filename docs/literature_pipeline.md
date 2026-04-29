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

## Phase 6B: Local Excerpt Packets

Local excerpts are short manually supplied text snippets. They are not full papers, not theorem verification, and not external data claims.

Keyword hints are non-binding cues. They are not verified labels and should not be promoted directly into seed rows.

Extraction packets are inputs for future LLM or manual extraction. Phase 6B makes no LLM calls and no web calls.

```powershell
python -m ihc_lab.cli build-literature-packets
```

This writes:

- `data/literature_queue/packets.sample.json`
- `reports/literature_packets.md`

## Phase 6C: Configurable LLM Extraction

Phase 6C adds a provider-agnostic extraction interface for local packets. The default provider is `mock`, which runs offline and is used by tests and CI.

```powershell
python -m ihc_lab.cli run-llm-extraction --provider mock
```

Manual JSON import works without API keys:

```powershell
python -m ihc_lab.cli import-manual-extraction --input data/literature_queue/manual_extraction.sample.json
```

Optional provider adapters are available for `anthropic` and `openai-compatible`, but external calls require `--allow-provider-call`. All LLM/manual outputs are force-reset to `llm_extracted_unverified` and `needs_human_review`.

See `docs/llm_configuration.md` for config files, environment variables, and provider safety notes.

## Phase 6D: Human Review and Controlled Promotion

Review decisions are stored in a manifest and applied to extracted rows:

```powershell
python -m ihc_lab.cli apply-literature-review
```

Accepted rows can then be exported as separate candidate `ObstructionChannel` records:

```powershell
python -m ihc_lab.cli export-reviewed-literature
```

The export writes `data/literature_queue/canonical_literature.candidates.json`.
It never modifies `data/seed_rows.json` automatically.

Default promotion keeps extracted rows as `llm_extracted_unverified` unless a controlled trust override is supplied. A `theorem_backed_literature` override requires reviewer notes, citation keys, and evidence snippets. Provider and manual outputs are not theorem verification.
