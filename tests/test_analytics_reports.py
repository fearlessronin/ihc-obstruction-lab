from pathlib import Path

from ihc_lab.analytics.channel_distribution import (
    channel_summary,
    channel_year_counts,
    collect_atlas_records,
    legitimacy_tier_summary,
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
from ihc_lab.cli import generate_analytics_report, main
from ihc_lab.reports import (
    channel_summary_latex,
    channel_summary_markdown,
    channel_year_distribution_markdown,
    family_channel_summary_markdown,
    family_legitimacy_summary_latex,
    family_legitimacy_summary_markdown,
    family_year_summary_latex,
    family_year_summary_markdown,
    legitimacy_tier_summary_latex,
    legitimacy_tier_summary_markdown,
)


def _analytics_payloads():
    records = collect_atlas_records()
    metadata = load_record_metadata()
    counts = channel_year_counts(records, metadata)
    summary = channel_summary(records, metadata)
    tiers = legitimacy_tier_summary(records, metadata)
    family_tiers = unique_family_tier_summary(records, metadata)
    family_years = unique_family_year_summary(records, metadata)
    family_channels = unique_family_channel_summary(records, metadata)
    return counts, summary, tiers, family_tiers, family_years, family_channels


def test_markdown_reports_contain_atlas_warning() -> None:
    counts, summary, tiers, family_tiers, family_years, family_channels = _analytics_payloads()

    assert "atlas-derived encoded-corpus counts" in channel_year_distribution_markdown(counts)
    assert "atlas-derived encoded-corpus counts" in channel_summary_markdown(summary)
    assert "atlas-derived encoded-corpus counts" in legitimacy_tier_summary_markdown(tiers)
    assert "atlas-derived encoded-corpus counts" in family_legitimacy_summary_markdown(family_tiers)
    assert "atlas-derived encoded-corpus counts" in family_year_summary_markdown(family_years)
    assert "atlas-derived encoded-corpus counts" in family_channel_summary_markdown(family_channels)


def test_family_markdown_reports_have_expected_titles() -> None:
    _, _, _, family_tiers, family_years, family_channels = _analytics_payloads()

    assert "# Unique-Family Legitimacy Summary" in family_legitimacy_summary_markdown(family_tiers)
    assert "# Unique-Family Year Summary" in family_year_summary_markdown(family_years)
    assert "# Unique-Family Channel Summary" in family_channel_summary_markdown(family_channels)


def test_latex_reports_contain_table() -> None:
    _, summary, tiers, family_tiers, family_years, _ = _analytics_payloads()

    assert r"\begin{table}" in channel_summary_latex(summary)
    assert r"\begin{table}" in legitimacy_tier_summary_latex(tiers)
    assert r"\begin{table}" in family_legitimacy_summary_latex(family_tiers)
    assert r"\begin{table}" in family_year_summary_latex(family_years)


def test_plotting_functions_create_png_files(tmp_path: Path) -> None:
    counts, _, tiers, family_tiers, _, _ = _analytics_payloads()
    stacked = tmp_path / "channel_year_stacked_bar.png"
    cumulative = tmp_path / "channel_cumulative_growth.png"
    tier_plot = tmp_path / "channel_legitimacy_tiers.png"
    family_tier_plot = tmp_path / "family_legitimacy_tiers.png"

    plot_channel_year_stacked_bar(counts, stacked)
    plot_channel_cumulative_growth(counts, cumulative)
    plot_channel_legitimacy_tiers(tiers, tier_plot)
    plot_family_legitimacy_tiers(family_tiers, family_tier_plot)

    assert stacked.exists()
    assert cumulative.exists()
    assert tier_plot.exists()
    assert family_tier_plot.exists()


def test_cli_analytics_report_creates_expected_reports_and_figures(tmp_path: Path) -> None:
    before = Path("data/seed_rows.json").read_bytes()
    paths = generate_analytics_report(output_dir=tmp_path)

    expected = {
        tmp_path / "channel_year_distribution.md",
        tmp_path / "channel_summary.md",
        tmp_path / "legitimacy_tier_summary.md",
        tmp_path / "family_legitimacy_summary.md",
        tmp_path / "family_year_summary.md",
        tmp_path / "family_channel_summary.md",
        tmp_path / "latex" / "channel_summary.tex",
        tmp_path / "latex" / "legitimacy_tier_summary.tex",
        tmp_path / "latex" / "family_legitimacy_summary.tex",
        tmp_path / "latex" / "family_year_summary.tex",
        tmp_path / "figures" / "channel_year_stacked_bar.png",
        tmp_path / "figures" / "channel_cumulative_growth.png",
        tmp_path / "figures" / "channel_legitimacy_tiers.png",
        tmp_path / "figures" / "family_legitimacy_tiers.png",
    }
    assert set(paths) == expected
    assert all(path.exists() for path in expected)
    assert Path("data/seed_rows.json").read_bytes() == before


def test_cli_analytics_report_command(tmp_path: Path) -> None:
    result = main(
        [
            "analytics-report",
            "--output-dir",
            str(tmp_path),
            "--count-mode",
            "family",
        ]
    )

    assert result == 0
    assert (tmp_path / "channel_year_distribution.md").exists()
    assert (tmp_path / "family_legitimacy_summary.md").exists()
    assert (tmp_path / "latex" / "family_year_summary.tex").exists()
    assert (tmp_path / "figures" / "channel_year_stacked_bar.png").exists()
    assert (tmp_path / "figures" / "family_legitimacy_tiers.png").exists()
