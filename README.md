# ihc-obstruction-lab

`ihc-obstruction-lab` is a research codebase for representing, validating, and reporting machine-readable obstruction-channel records for the integral Hodge conjecture.

It supports the paper project:

> "Obstruction Channels and Generator Mechanisms for the Integral Hodge Conjecture."

This repository does not prove new counterexamples automatically. It provides a reproducible schema, validation layer, and seed dataset for known and candidate obstruction mechanisms: local discriminant packages, shadow selectors, torsion trajectories, finite-coefficient cup-product Bockstein candidates, lattice-saturation records, nodal free-relation channels, and proof bottlenecks.

## Release Status

Current release: `v0.1.0`.

This release includes the obstruction-channel schema, 12-row seed corpus, validation layer, reports, classifier, feature extraction, association-rule mining, formal candidate generation, bottleneck ranking, and CI-backed pytest coverage.

## Installation

Use Python 3.11 or newer.

```powershell
pip install -e ".[dev]"
pytest
```

## Repository Layout

```text
src/ihc_lab/      Python package with data models, validation, dataset IO, and reports
data/             Machine-readable seed rows plus schema notes
docs/             Human-readable notes on channels and the seed dataset
tests/            Pytest coverage for groups, shadows, cup products, validation, and seed rows
notebooks/        Reserved for exploratory notebooks
```

## Obstruction Channels

An obstruction channel is a structured record describing how a geometric or cohomological package may contribute to an integral Hodge obstruction workflow. A row records its trust level, computability level, active operations, survival status, obstruction status, citation keys, and any attached structured package such as a finite local discriminant group or finite-coefficient cup product candidate.

The dataset intentionally distinguishes theorem-backed rows from generated candidates. Candidate rows must name their proof bottleneck; LLM-extracted rows must not be treated as theorem-backed data without independent verification.

## Seed Dataset

The initial seed dataset lives in `data/seed_rows.json`. It includes calibration rows for local discriminant packages, a Coble order-two shadow selector, nodal free-relation rows, a Benoist-Ottem benchmark row, a Diaz level-two finite-coefficient Bockstein row, and a level-three Coble-Diaz candidate row.

The supplied citation keys are placeholders for verified bibliography work. Do not expand them into full citation metadata unless the bibliographic details have been checked.

## Load Seed Rows

```python
from ihc_lab.datasets import load_seed_rows

records = load_seed_rows()
print(len(records))
print(records[0].markdown_summary())
```

## Check Diaz Degree/Twist Validity

```python
from ihc_lab.datasets import load_seed_rows

records = load_seed_rows()
diaz = next(row for row in records if row.id == "diaz_level_two")
candidate = diaz.cup_product_candidate

assert candidate is not None
print(candidate.total_degree())
print(candidate.total_twist())
print(candidate.is_degree_twist_valid())
print(candidate.bockstein_target_string())
```

## Dataset Summary

```python
from ihc_lab.datasets import load_seed_rows
from ihc_lab.reports import dataset_summary_markdown

records = load_seed_rows()
print(dataset_summary_markdown(records))
```

## Generating Reports

Markdown and LaTeX reports are generated deterministically from `data/seed_rows.json`:

```powershell
python -m ihc_lab.cli generate-reports
```

The command writes Markdown reports into `reports/` and LaTeX table fragments into `reports/latex/`. These outputs are intended to support the paper's Seed Dataset and Channel Calibration section.

For full reproduction notes, see `docs/reproducibility.md`.

## Exploratory Association-Rule Reports

The same report command also generates feature-matrix and association-rule reports:

```powershell
python -m ihc_lab.cli generate-reports
```

Association rules are exploratory and not theorem-proving. They are used to recover mechanism signatures from the hand-verified seed corpus, such as links between package features, operations, channel labels, obstruction statuses, and bottlenecks.

## Generating Candidate Reports

The report command also emits generated formal candidates and bottleneck-priority reports:

```powershell
python -m ihc_lab.cli generate-reports
```

Generated candidates are formal proof targets. They are not new counterexamples, and the priority score is not a truth probability. The score is a compact research-priority heuristic for comparing formal validity, theorem analogy, survival bottlenecks, computability, and motivic-lift compatibility.

## Non-Claims

Generated candidates are proof targets, not theorem-backed counterexamples. Priority scores are research-priority scores, not probabilities of truth. Theorem-backed status requires citation and human verification.

See `docs/non_claims.md` for the concise release policy.

## Literature Review Queue

Phase 6A includes a scaffold for future LLM-assisted literature extraction. No LLM calls are made, no network access is used, and all extracted rows remain unverified until human review.

```powershell
python -m ihc_lab.cli literature-report
```

Local packet generation for future manual/LLM extraction also runs without external calls:

```powershell
python -m ihc_lab.cli build-literature-packets
```

Keyword hints in packets are not verified labels.

See `docs/literature_pipeline.md` for the queue workflow and promotion rules.

Pilot source metadata for atlas expansion can be summarized with:

```powershell
python -m ihc_lab.cli pilot-sources-report
```

## Configurable LLM Extraction

Phase 6C adds mock, manual, OpenAI-compatible, and Anthropic provider interfaces for local extraction packets. Mock mode is offline and is the default testing path:

```powershell
python -m ihc_lab.cli run-llm-extraction --provider mock
python -m ihc_lab.cli import-manual-extraction --input data/literature_queue/manual_extraction.sample.json
```

Provider mode is optional, uses user-owned API keys, and requires `--allow-provider-call`. Provider mode requires user-owned API keys; the repository does not provide shared keys. All LLM/manual outputs remain unverified and queued for human review.

See `docs/llm_configuration.md` for configuration details.

## Literature Review and Promotion

Human review decisions can be applied and exported without modifying `data/seed_rows.json`:

```powershell
python -m ihc_lab.cli apply-literature-review
python -m ihc_lab.cli export-reviewed-literature
```

Reviewed exports go to `data/literature_queue/canonical_literature.candidates.json`.

## Canonical Literature Rows

Manually curated canonical literature mechanism anchors are stored separately from seed rows in `data/canonical_literature_rows.json`. They can be reported with:

```powershell
python -m ihc_lab.cli canonical-literature-report
```

## Analytics Reports

Temporal channel-distribution analytics use `data/analytics/record_metadata.json` as an overlay, leaving `data/seed_rows.json` unchanged. Counts are atlas-derived encoded-corpus counts, not complete literature counts.

The analytics distinguish channel-level counts from unique-family counts to avoid double-counting multi-channel mechanisms.

```powershell
python -m ihc_lab.cli analytics-report
```

The command writes Markdown summaries, LaTeX tables, and PNG figures under `reports/`, including `reports/theorem_backed_family_summary.md`.

## Local/Remote Sync

This repository is intended to be developed locally and kept in sync with GitHub:

```powershell
git pull --rebase origin main
python -m pytest -q
git add -A
git commit -m "Describe the research-codebase change"
git push origin main
```

Run tests before pushing changes that alter models, validation behavior, seed rows, or reports.

## Development Notes

The package favors explicit, readable data models over automated theorem inference. New validation rules should come with tests, and seed rows should stay close to cited or explicitly marked candidate mechanisms.

Do not add machine-learning workflows, web crawlers, or unverified theorem extraction to this initial layer. The first goal is a reproducible schema and carefully labeled seed data.
