# Analytics

Phase 7A adds temporal channel-distribution analytics for the encoded obstruction-channel atlas.

The reports are atlas-derived encoded-corpus counts. They are not complete counts of all known integral Hodge conjecture counterexamples, mechanisms, or papers.

## Metadata Overlay

Analytics metadata lives in `data/analytics/record_metadata.json`. This overlay stores publication years, primary references, family identifiers, primary-family flags, and count flags without modifying `data/seed_rows.json`.

## Count Modes

- `row`: counts every record-channel pair.
- `family`: de-duplicates by `(family_id, channel, legitimacy tier)`.

Family mode is the default because several rows represent generated references, templates, or variants within a single mechanism family.

## Channel Counts Versus Unique-Family Counts

Channel-level reports count a family once for each channel it occupies. For example, a single multi-channel mechanism may contribute to several channel columns.

Unique-family reports count each `family_id` once, independent of how many channels the family occupies.

Use channel-level counts to see mechanism-channel coverage. Use unique-family counts to estimate how many distinct obstruction, boundary, benchmark, or candidate families are represented.

Both views are atlas-derived and incomplete with respect to the full literature.

## Strict vs Extended Counts

Strict mode includes only theorem-backed obstruction rows.

Extended mode includes theorem-backed obstructions, computed benchmarks, boundary/calibration rows, generated candidates, and unverified extracted rows if they are included explicitly.

## Legitimacy Tiers

Rows are assigned to these tiers:

- `theorem_backed_obstruction`
- `computed_benchmark`
- `boundary_or_calibration`
- `reviewed_candidate`
- `generated_candidate`
- `unverified_extracted`
- `unknown`

## Running Reports

```powershell
python -m ihc_lab.cli analytics-report
```

Use row counts:

```powershell
python -m ihc_lab.cli analytics-report --count-mode row
```

Use strict theorem-backed obstruction counts:

```powershell
python -m ihc_lab.cli analytics-report --strict
```
