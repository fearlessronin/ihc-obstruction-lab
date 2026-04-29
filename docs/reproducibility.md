# Reproducibility

This release is designed to regenerate its dataset-derived artifacts from the checked-in seed corpus.

## Install

```powershell
pip install -e ".[dev]"
```

## Run Tests

```powershell
python -m pytest -q
```

Expected status at v0.1.0: 40 passing tests.

## Generate Reports

```powershell
python -m ihc_lab.cli generate-reports
```

## Generate Analytics Reports

```powershell
python -m ihc_lab.cli analytics-report
```

## Generated Artifacts

The report command writes:

- `data/generated_candidates.json`
- `reports/*.md`
- `reports/latex/*.tex`
- `reports/figures/*.png`

The report outputs derive from `data/seed_rows.json` and the formal candidates generated from those seed rows. The generated candidate file is reproducible from the CLI and should not be treated as an external data source.
