"""Command-line interface for IHC obstruction lab utilities."""

from __future__ import annotations

import argparse
from pathlib import Path

from ihc_lab.candidate_generator import generate_all_candidates
from ihc_lab.datasets import load_seed_rows, save_seed_rows
from ihc_lab.literature.ingestion import load_excerpt_txt
from ihc_lab.literature.packet_builder import build_packets, save_packets_json
from ihc_lab.literature.reports import (
    literature_packets_markdown,
    literature_queue_latex,
    literature_queue_markdown,
)
from ihc_lab.literature.review_queue import load_review_queue
from ihc_lab.literature.sources import load_literature_sources
from ihc_lab.ranking import rank_candidates
from ihc_lab.reports import (
    association_rules_latex,
    association_rules_markdown,
    bottleneck_summary_latex,
    bottleneck_table_markdown,
    candidate_generation_latex,
    candidate_generation_markdown,
    channel_table_latex,
    channel_table_markdown,
    classifier_report_latex,
    classifier_report_markdown,
    coble_diaz_hierarchy_latex,
    cup_product_validation_latex,
    cup_product_validation_markdown,
    dataset_summary_markdown,
    feature_matrix_markdown,
    feature_summary_latex,
    seed_dataset_summary_latex,
)


def generate_reports(data_path: str | Path, output_dir: str | Path) -> list[Path]:
    records = load_seed_rows(data_path)
    candidates = generate_all_candidates(records, max_level=5)
    candidate_scores = rank_candidates(candidates)
    report_dir = Path(output_dir)
    latex_dir = report_dir / "latex"
    report_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)
    candidate_output_path = Path(data_path).parent / "generated_candidates.json"
    save_seed_rows(candidates, candidate_output_path)

    outputs: dict[Path, str] = {
        report_dir / "seed_dataset_summary.md": dataset_summary_markdown(records),
        report_dir / "channel_table.md": "# Channel Table\n\n" + channel_table_markdown(records),
        report_dir / "bottleneck_summary.md": (
            "# Bottleneck Summary\n\n" + bottleneck_table_markdown(records)
        ),
        report_dir / "cup_product_validation.md": cup_product_validation_markdown(records),
        report_dir / "classifier_report.md": classifier_report_markdown(records),
        report_dir / "feature_matrix.md": feature_matrix_markdown(records),
        report_dir / "association_rules.md": association_rules_markdown(records),
        report_dir / "candidate_generation.md": candidate_generation_markdown(
            candidates, candidate_scores
        ),
        latex_dir / "seed_dataset_summary.tex": seed_dataset_summary_latex(records),
        latex_dir / "channel_table.tex": channel_table_latex(records),
        latex_dir / "bottleneck_summary.tex": bottleneck_summary_latex(records),
        latex_dir / "cup_product_validation.tex": cup_product_validation_latex(records),
        latex_dir / "classifier_report.tex": classifier_report_latex(records),
        latex_dir / "feature_summary.tex": feature_summary_latex(records),
        latex_dir / "association_rules.tex": association_rules_latex(records),
        latex_dir / "candidate_generation.tex": candidate_generation_latex(
            candidates, candidate_scores
        ),
        latex_dir / "coble_diaz_hierarchy.tex": coble_diaz_hierarchy_latex(candidates),
    }

    for path, content in outputs.items():
        path.write_text(content + "\n", encoding="utf-8")

    return [candidate_output_path, *list(outputs)]


def generate_literature_report(
    raw_sources_path: str | Path,
    extracted_rows_path: str | Path,
    output_dir: str | Path,
) -> list[Path]:
    queue = load_review_queue(raw_sources_path, extracted_rows_path)
    report_dir = Path(output_dir)
    latex_dir = report_dir / "latex"
    report_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        report_dir / "literature_queue.md": literature_queue_markdown(queue),
        latex_dir / "literature_queue.tex": literature_queue_latex(queue),
    }
    for path, content in outputs.items():
        path.write_text(content + "\n", encoding="utf-8")
    return list(outputs)


def _source_id_for_sample_excerpt(path: Path) -> str:
    sample_mapping = {
        "sample_colliot_theleme_voisin_excerpt": "colliot_theleme_voisin_2012_unramified",
        "sample_fermat_computation_excerpt": "aljovin_movasati_villaflor_2019_fermat",
    }
    return sample_mapping.get(path.stem, path.stem)


def build_literature_packets(
    sources_path: str | Path,
    excerpts_dir: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> list[Path]:
    sources = load_literature_sources(sources_path)
    excerpt_paths = sorted(Path(excerpts_dir).glob("*.txt"))
    excerpts = [
        load_excerpt_txt(
            path,
            source_id=_source_id_for_sample_excerpt(path),
            section_label="sample excerpt",
            notes="Local sample excerpt for packet generation.",
        )
        for path in excerpt_paths
    ]
    packets = build_packets(sources, excerpts)
    save_packets_json(packets, output_path)

    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(literature_packets_markdown(packets) + "\n", encoding="utf-8")
    return [Path(output_path), report]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ihc-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-reports")
    generate.add_argument("--data-path", default="data/seed_rows.json")
    generate.add_argument("--output-dir", default="reports")

    literature = subparsers.add_parser("literature-report")
    literature.add_argument(
        "--raw-sources-path",
        default="data/literature_queue/raw_sources.sample.json",
    )
    literature.add_argument(
        "--extracted-rows-path",
        default="data/literature_queue/extracted_rows.sample.json",
    )
    literature.add_argument("--output-dir", default="reports")

    packets = subparsers.add_parser("build-literature-packets")
    packets.add_argument("--sources", default="data/literature_queue/raw_sources.sample.json")
    packets.add_argument("--excerpts-dir", default="data/literature_queue/excerpts")
    packets.add_argument("--output", default="data/literature_queue/packets.sample.json")
    packets.add_argument("--report", default="reports/literature_packets.md")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate-reports":
        paths = generate_reports(args.data_path, args.output_dir)
        for path in paths:
            print(path)
        return 0
    if args.command == "literature-report":
        paths = generate_literature_report(
            args.raw_sources_path,
            args.extracted_rows_path,
            args.output_dir,
        )
        for path in paths:
            print(path)
        return 0
    if args.command == "build-literature-packets":
        paths = build_literature_packets(
            args.sources,
            args.excerpts_dir,
            args.output,
            args.report,
        )
        for path in paths:
            print(path)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
