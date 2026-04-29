"""Matplotlib figures for atlas analytics."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path


def _pyplot():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _numeric_rows(counts: list[dict]) -> list[dict]:
    return [row for row in counts if isinstance(row["year"], int)]


def plot_channel_year_stacked_bar(counts: list[dict], output_path: str | Path) -> None:
    plt = _pyplot()
    rows = _numeric_rows(counts)
    years = sorted({row["year"] for row in rows})
    channels = sorted({row["channel"] for row in rows})
    by_channel_year = defaultdict(int)
    for row in rows:
        by_channel_year[(row["channel"], row["year"])] += row["count"]

    fig, ax = plt.subplots(figsize=(10, 5))
    bottoms = [0] * len(years)
    for channel in channels:
        values = [by_channel_year[(channel, year)] for year in years]
        ax.bar(years, values, bottom=bottoms, label=channel)
        bottoms = [left + right for left, right in zip(bottoms, values)]
    ax.set_title("Atlas-derived channel counts by year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    ax.legend(fontsize="x-small")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_channel_cumulative_growth(counts: list[dict], output_path: str | Path) -> None:
    plt = _pyplot()
    rows = _numeric_rows(counts)
    years = sorted({row["year"] for row in rows})
    channels = sorted({row["channel"] for row in rows})
    by_channel_year = defaultdict(int)
    for row in rows:
        by_channel_year[(row["channel"], row["year"])] += row["count"]

    fig, ax = plt.subplots(figsize=(10, 5))
    for channel in channels:
        total = 0
        values: list[int] = []
        for year in years:
            total += by_channel_year[(channel, year)]
            values.append(total)
        ax.plot(years, values, marker="o", label=channel)
    ax.set_title("Cumulative atlas-derived channel counts")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative count")
    ax.legend(fontsize="x-small")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_channel_legitimacy_tiers(tier_summary: list[dict], output_path: str | Path) -> None:
    plt = _pyplot()
    tiers = [row["tier"] for row in tier_summary]
    counts = [row["count"] for row in tier_summary]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(tiers, counts)
    ax.set_title("Atlas-derived rows by legitimacy tier")
    ax.set_xlabel("Legitimacy tier")
    ax.set_ylabel("Count")
    ax.tick_params(axis="x", rotation=35)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_family_legitimacy_tiers(summary: list[dict], output_path: str | Path) -> None:
    plt = _pyplot()
    tiers = [row["tier"] for row in summary]
    counts = [row["family_count"] for row in summary]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(tiers, counts)
    ax.set_title("Unique mechanism families by legitimacy tier")
    ax.set_xlabel("Legitimacy tier")
    ax.set_ylabel("Family count")
    ax.tick_params(axis="x", rotation=35)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)
