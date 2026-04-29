"""Command-line interface for IHC obstruction lab utilities."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ihc_lab.analytics.channel_distribution import (
    channel_summary,
    channel_year_counts,
    collect_atlas_records,
    legitimacy_tier_summary,
    theorem_backed_family_summary,
    total_unique_families,
    unique_family_channel_summary,
    unique_family_tier_summary,
    unique_family_year_summary,
)
from ihc_lab.analytics.metadata import load_record_metadata
from ihc_lab.analytics.plotting import (
    plot_channel_cumulative_growth,
    plot_channel_legitimacy_tiers,
    plot_channel_year_stacked_bar,
    plot_family_legitimacy_tiers,
)
from ihc_lab.candidate_generator import generate_all_candidates
from ihc_lab.datasets import (
    load_canonical_literature_rows,
    load_seed_rows,
    save_seed_rows,
)
from ihc_lab.literature.extraction_schema import (
    load_extracted_candidates,
    save_extracted_candidates,
)
from ihc_lab.literature.extract_with_llm import extract_candidates_from_packets
from ihc_lab.literature.ingestion import load_excerpt_txt
from ihc_lab.literature.llm_client import create_llm_client
from ihc_lab.literature.llm_config import LLMConfig, load_llm_config
from ihc_lab.literature.manual_import import import_manual_extraction
from ihc_lab.literature.packet_builder import build_packets, load_packets_json, save_packets_json
from ihc_lab.literature.pilot_sources import (
    load_pilot_sources_csv,
    load_pilot_sources_json,
)
from ihc_lab.literature.promotion import (
    export_promoted_candidates,
    promote_reviewed_candidates,
)
from ihc_lab.literature.review_actions import (
    apply_review_decisions,
    load_review_decisions,
)
from ihc_lab.literature.reports import (
    llm_extraction_report_markdown,
    literature_packets_markdown,
    literature_queue_latex,
    literature_queue_markdown,
    pilot_source_channel_intents_markdown,
    pilot_sources_summary_latex,
    pilot_sources_summary_markdown,
    promoted_candidates_markdown,
    review_status_report_markdown,
)
from ihc_lab.literature.review_queue import load_review_queue
from ihc_lab.literature.source_import import (
    convert_pilot_sources_to_literature_sources,
    merge_sources,
)
from ihc_lab.literature.sources import load_literature_sources, save_literature_sources
from ihc_lab.ranking import rank_candidates
from ihc_lab.reports import (
    association_rules_latex,
    association_rules_markdown,
    bottleneck_summary_latex,
    bottleneck_table_markdown,
    candidate_generation_latex,
    candidate_generation_markdown,
    canonical_literature_table_latex,
    canonical_literature_table_markdown,
    channel_summary_latex,
    channel_summary_markdown,
    channel_year_distribution_markdown,
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
    family_channel_summary_markdown,
    family_legitimacy_summary_latex,
    family_legitimacy_summary_markdown,
    family_year_summary_latex,
    family_year_summary_markdown,
    legitimacy_tier_summary_latex,
    legitimacy_tier_summary_markdown,
    seed_dataset_summary_latex,
    theorem_backed_family_summary_latex,
    theorem_backed_family_summary_markdown,
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

    canonical_path = Path("data/canonical_literature_rows.json")
    canonical_outputs: dict[Path, str] = {}
    if canonical_path.exists():
        canonical_rows = load_canonical_literature_rows(canonical_path)
        canonical_outputs = {
            report_dir / "canonical_literature_table.md": (
                canonical_literature_table_markdown(canonical_rows)
            ),
            latex_dir / "canonical_literature_table.tex": (
                canonical_literature_table_latex(canonical_rows)
            ),
        }
        for path, content in canonical_outputs.items():
            path.write_text(content + "\n", encoding="utf-8")

    return [candidate_output_path, *list(outputs), *list(canonical_outputs)]


def generate_canonical_literature_report(
    data_path: str | Path,
    output_dir: str | Path,
) -> list[Path]:
    records = load_canonical_literature_rows(data_path)
    report_dir = Path(output_dir)
    latex_dir = report_dir / "latex"
    report_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        report_dir / "canonical_literature_table.md": (
            canonical_literature_table_markdown(records)
        ),
        latex_dir / "canonical_literature_table.tex": (
            canonical_literature_table_latex(records)
        ),
    }
    for path, content in outputs.items():
        path.write_text(content + "\n", encoding="utf-8")
    return list(outputs)


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


def _config_with_provider(config: LLMConfig, provider: str | None) -> LLMConfig:
    if provider is None:
        return config
    data = config.to_dict()
    previous_provider = data["provider"]
    data["provider"] = provider
    if provider != previous_provider:
        data["api_key_env"] = None
    return LLMConfig.from_dict(data)


def run_llm_extraction(
    provider: str | None,
    config_path: str | Path | None,
    packets_path: str | Path,
    output_path: str | Path | None,
    report_path: str | Path,
    allow_provider_call: bool,
) -> list[Path]:
    config = _config_with_provider(load_llm_config(config_path), provider)
    if config.provider in {"openai-compatible", "anthropic"} and not allow_provider_call:
        raise RuntimeError(
            "Provider calls are disabled by default. Pass --allow-provider-call to use external LLM APIs."
        )
    output = Path(
        output_path
        or (
            "data/literature_queue/extracted_rows.mock.json"
            if config.provider == "mock"
            else "data/literature_queue/extracted_rows.llm.json"
        )
    )
    packets = load_packets_json(packets_path)
    client = create_llm_client(config)
    candidates = extract_candidates_from_packets(packets, client)
    save_extracted_candidates(candidates, output)

    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(llm_extraction_report_markdown(candidates) + "\n", encoding="utf-8")
    return [output, report]


def run_manual_import(
    input_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> list[Path]:
    candidates = import_manual_extraction(input_path, output_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(llm_extraction_report_markdown(candidates) + "\n", encoding="utf-8")
    return [Path(output_path), report]


def apply_literature_review(
    extracted_path: str | Path,
    review_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
) -> list[Path]:
    candidates = load_extracted_candidates(extracted_path)
    decisions = load_review_decisions(review_path)
    reviewed = apply_review_decisions(candidates, decisions)
    save_extracted_candidates(reviewed, output_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(review_status_report_markdown(reviewed) + "\n", encoding="utf-8")
    return [Path(output_path), report]


def export_reviewed_literature(
    reviewed_path: str | Path,
    output_path: str | Path,
    report_path: str | Path,
    trust_overrides_path: str | Path | None = None,
) -> list[Path]:
    candidates = load_extracted_candidates(reviewed_path)
    overrides: dict[str, str] | None = None
    if trust_overrides_path is not None:
        with Path(trust_overrides_path).open("r", encoding="utf-8") as handle:
            overrides = json.load(handle)
    promoted = promote_reviewed_candidates(candidates, overrides)
    export_promoted_candidates(promoted, output_path)
    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(promoted_candidates_markdown(promoted) + "\n", encoding="utf-8")
    return [Path(output_path), report]


def generate_pilot_sources_report(
    input_path: str | Path,
    csv_path: str | Path | None,
    merge_into_queue: bool,
    queue_output: str | Path,
    report_path: str | Path,
    channel_report_path: str | Path,
    latex_path: str | Path,
) -> list[Path]:
    sources = (
        load_pilot_sources_csv(csv_path)
        if csv_path is not None
        else load_pilot_sources_json(input_path)
    )
    report = Path(report_path)
    channel_report = Path(channel_report_path)
    latex = Path(latex_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    channel_report.parent.mkdir(parents=True, exist_ok=True)
    latex.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(pilot_sources_summary_markdown(sources) + "\n", encoding="utf-8")
    channel_report.write_text(
        pilot_source_channel_intents_markdown(sources) + "\n",
        encoding="utf-8",
    )
    latex.write_text(pilot_sources_summary_latex(sources) + "\n", encoding="utf-8")
    outputs = [report, channel_report, latex]

    if merge_into_queue:
        queue_path = Path("data/literature_queue/raw_sources.sample.json")
        existing = load_literature_sources(queue_path) if queue_path.exists() else []
        merged = merge_sources(existing, convert_pilot_sources_to_literature_sources(sources))
        save_literature_sources(merged, queue_output)
        outputs.append(Path(queue_output))
    return outputs


def generate_analytics_report(
    count_mode: str = "family",
    strict: bool = False,
    include_promoted: bool = False,
    metadata_path: str | Path = "data/analytics/record_metadata.json",
    figures: bool = True,
    output_dir: str | Path = "reports",
) -> list[Path]:
    records = collect_atlas_records(include_promoted=include_promoted)
    metadata = load_record_metadata(metadata_path)
    counts = channel_year_counts(records, metadata, count_mode=count_mode, strict=strict)
    summary = channel_summary(records, metadata, count_mode=count_mode)
    tier_summary = legitimacy_tier_summary(records, metadata, count_mode=count_mode)
    family_tier_summary = unique_family_tier_summary(records, metadata, strict=strict)
    family_year_summary = unique_family_year_summary(records, metadata, strict=strict)
    family_channel_summary = unique_family_channel_summary(records, metadata, strict=strict)
    total_families = total_unique_families(records, metadata, strict=strict)
    theorem_families = theorem_backed_family_summary(records, metadata)
    report_dir = Path(output_dir)
    latex_dir = report_dir / "latex"
    figure_dir = report_dir / "figures"
    report_dir.mkdir(parents=True, exist_ok=True)
    latex_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        report_dir / "channel_year_distribution.md": channel_year_distribution_markdown(
            counts
        ),
        report_dir / "channel_summary.md": channel_summary_markdown(summary),
        report_dir / "legitimacy_tier_summary.md": legitimacy_tier_summary_markdown(
            tier_summary
        ),
        report_dir / "family_legitimacy_summary.md": family_legitimacy_summary_markdown(
            family_tier_summary,
            total_unique_families=total_families,
        ),
        report_dir / "family_year_summary.md": family_year_summary_markdown(
            family_year_summary
        ),
        report_dir / "family_channel_summary.md": family_channel_summary_markdown(
            family_channel_summary
        ),
        report_dir / "theorem_backed_family_summary.md": (
            theorem_backed_family_summary_markdown(theorem_families)
        ),
        latex_dir / "channel_summary.tex": channel_summary_latex(summary),
        latex_dir / "legitimacy_tier_summary.tex": legitimacy_tier_summary_latex(
            tier_summary
        ),
        latex_dir / "family_legitimacy_summary.tex": (
            family_legitimacy_summary_latex(
                family_tier_summary,
                total_unique_families=total_families,
            )
        ),
        latex_dir / "family_year_summary.tex": family_year_summary_latex(
            family_year_summary
        ),
        latex_dir / "theorem_backed_family_summary.tex": (
            theorem_backed_family_summary_latex(theorem_families)
        ),
    }
    for path, content in outputs.items():
        path.write_text(content + "\n", encoding="utf-8")

    paths = list(outputs)
    if figures:
        figure_dir.mkdir(parents=True, exist_ok=True)
        figure_paths = [
            figure_dir / "channel_year_stacked_bar.png",
            figure_dir / "channel_cumulative_growth.png",
            figure_dir / "channel_legitimacy_tiers.png",
            figure_dir / "family_legitimacy_tiers.png",
        ]
        plot_channel_year_stacked_bar(counts, figure_paths[0])
        plot_channel_cumulative_growth(counts, figure_paths[1])
        plot_channel_legitimacy_tiers(tier_summary, figure_paths[2])
        plot_family_legitimacy_tiers(family_tier_summary, figure_paths[3])
        paths.extend(figure_paths)
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ihc-lab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate-reports")
    generate.add_argument("--data-path", default="data/seed_rows.json")
    generate.add_argument("--output-dir", default="reports")

    canonical = subparsers.add_parser("canonical-literature-report")
    canonical.add_argument("--data-path", default="data/canonical_literature_rows.json")
    canonical.add_argument("--output-dir", default="reports")

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

    llm = subparsers.add_parser("run-llm-extraction")
    llm.add_argument("--provider", choices=["mock", "openai-compatible", "anthropic"])
    llm.add_argument("--config")
    llm.add_argument("--packets", default="data/literature_queue/packets.sample.json")
    llm.add_argument("--output")
    llm.add_argument("--report", default="reports/literature_llm_extraction.md")
    llm.add_argument("--allow-provider-call", action="store_true")

    manual = subparsers.add_parser("import-manual-extraction")
    manual.add_argument("--input", default="data/literature_queue/manual_extraction.json")
    manual.add_argument("--output", default="data/literature_queue/extracted_rows.manual.json")
    manual.add_argument("--report", default="reports/literature_manual_extraction.md")

    review = subparsers.add_parser("apply-literature-review")
    review.add_argument("--extracted", default="data/literature_queue/extracted_rows.manual.json")
    review.add_argument("--review", default="data/literature_queue/review_manifest.sample.json")
    review.add_argument("--output", default="data/literature_queue/extracted_rows.reviewed.json")
    review.add_argument("--report", default="reports/literature_review_status.md")

    export = subparsers.add_parser("export-reviewed-literature")
    export.add_argument("--reviewed", default="data/literature_queue/extracted_rows.reviewed.json")
    export.add_argument(
        "--output",
        default="data/literature_queue/canonical_literature.candidates.json",
    )
    export.add_argument("--report", default="reports/promoted_literature_candidates.md")
    export.add_argument("--trust-overrides")

    analytics = subparsers.add_parser("analytics-report")
    analytics.add_argument("--count-mode", choices=["row", "family"], default="family")
    analytics.add_argument("--strict", action="store_true")
    analytics.add_argument("--include-promoted", action="store_true")
    analytics.add_argument("--metadata", default="data/analytics/record_metadata.json")
    analytics.add_argument("--figures", dest="figures", action="store_true", default=True)
    analytics.add_argument("--no-figures", dest="figures", action="store_false")
    analytics.add_argument("--output-dir", default="reports")

    pilot = subparsers.add_parser("pilot-sources-report")
    pilot.add_argument(
        "--input",
        default="data/literature_queue/pilot_sources/pilot_sources.sample.json",
    )
    pilot.add_argument("--csv")
    pilot.add_argument("--merge-into-queue", action="store_true")
    pilot.add_argument("--queue-output", default="data/literature_queue/raw_sources.pilot.json")
    pilot.add_argument("--report", default="reports/pilot_sources_summary.md")
    pilot.add_argument("--channel-report", default="reports/pilot_source_channel_intents.md")
    pilot.add_argument("--latex", default="reports/latex/pilot_sources_summary.tex")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate-reports":
        paths = generate_reports(args.data_path, args.output_dir)
        for path in paths:
            print(path)
        return 0
    if args.command == "canonical-literature-report":
        paths = generate_canonical_literature_report(args.data_path, args.output_dir)
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
    if args.command == "run-llm-extraction":
        paths = run_llm_extraction(
            args.provider,
            args.config,
            args.packets,
            args.output,
            args.report,
            args.allow_provider_call,
        )
        for path in paths:
            print(path)
        return 0
    if args.command == "import-manual-extraction":
        paths = run_manual_import(args.input, args.output, args.report)
        for path in paths:
            print(path)
        return 0
    if args.command == "apply-literature-review":
        paths = apply_literature_review(
            args.extracted,
            args.review,
            args.output,
            args.report,
        )
        for path in paths:
            print(path)
        return 0
    if args.command == "export-reviewed-literature":
        paths = export_reviewed_literature(
            args.reviewed,
            args.output,
            args.report,
            args.trust_overrides,
        )
        for path in paths:
            print(path)
        return 0
    if args.command == "analytics-report":
        paths = generate_analytics_report(
            count_mode=args.count_mode,
            strict=args.strict,
            include_promoted=args.include_promoted,
            metadata_path=args.metadata,
            figures=args.figures,
            output_dir=args.output_dir,
        )
        for path in paths:
            print(path)
        return 0
    if args.command == "pilot-sources-report":
        paths = generate_pilot_sources_report(
            args.input,
            args.csv,
            args.merge_into_queue,
            args.queue_output,
            args.report,
            args.channel_report,
            args.latex,
        )
        for path in paths:
            print(path)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
