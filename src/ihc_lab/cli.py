"""Command-line interface for IHC obstruction lab utilities."""

from __future__ import annotations

import argparse
from pathlib import Path

from ihc_lab.datasets import load_seed_rows
from ihc_lab.reports import (
    bottleneck_summary_latex,
    bottleneck_table_markdown,
    channel_table_latex,
    channel_table_markdown,
    classifier_report_latex,
    classifier_report_markdown,
    cup_product_validation_latex,
    cup_product_validation_markdown,
    dataset_summary_markdown,
    seed_dataset_summary_latex,
)


def generate_reports(data_path: str | Path, output_dir: str | Path) -> list[Path]:
    records = load_seed_rows(data_path)
    report_dir = Path(output_dir)
    latex_dir = report_dir / "latex"
    report_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[Path, str] = {
        report_dir / "seed_dataset_summary.md": dataset_summary_markdown(records),
        report_dir / "channel_table.md": "# Channel Table\n\n" + channel_table_markdown(records),
        report_dir / "bottleneck_summary.md": (
            "# Bottleneck Summary\n\n" + bottleneck_table_markdown(records)
        ),
        report_dir / "cup_product_validation.md": cup_product_validation_markdown(records),
        report_dir / "classifier_report.md": classifier_report_markdown(records),
        latex_dir / "seed_dataset_summary.tex": seed_dataset_summary_latex(records),
        latex_dir / "channel_table.tex": channel_table_latex(records),
        latex_dir / "bottleneck_summary.tex": bottleneck_summary_latex(records),
        latex_dir / "cup_product_validation.tex": cup_product_validation_latex(records),
        latex_dir / "classifier_report.tex": classifier_report_latex(records),
    }

    for path, content in outputs.items():
        path.write_text(content + "\n", encoding="utf-8")

    return list(outputs)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ihc-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-reports")
    generate.add_argument("--data-path", default="data/seed_rows.json")
    generate.add_argument("--output-dir", default="reports")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate-reports":
        paths = generate_reports(args.data_path, args.output_dir)
        for path in paths:
            print(path)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
