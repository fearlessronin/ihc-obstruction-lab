from ihc_lab.candidate_generator import generate_coble_diaz_level_candidates
from ihc_lab.enums import ObstructionStatus
from ihc_lab.ranking import rank_candidates, score_candidate
from ihc_lab.reports import (
    candidate_generation_latex,
    candidate_generation_markdown,
    coble_diaz_hierarchy_latex,
)


def test_score_candidate_level_three() -> None:
    candidates = generate_coble_diaz_level_candidates(max_level=5)
    level_three = next(candidate for candidate in candidates if "level_3" in candidate.id)
    score = score_candidate(level_three)

    assert score.score > 0
    assert score.bottleneck == "unramified_nonvanishing"
    assert (
        "Research-priority" in score.explanation
        or "Formal validity" in score.explanation
        or "survival bottleneck" in score.explanation
    )


def test_rank_candidates_sorted_and_labels() -> None:
    candidates = generate_coble_diaz_level_candidates(max_level=5)
    scores = rank_candidates(candidates)

    assert scores == sorted(scores, key=lambda item: (-item.score, item.record_id))
    assert scores[0].record_id == "diaz_level_2_generated_or_reference"
    assert all(
        candidate.obstruction_status != ObstructionStatus.theorem_backed_obstruction
        for candidate in candidates
        if candidate.id != "diaz_level_2_generated_or_reference"
    )


def test_candidate_reports_render() -> None:
    candidates = generate_coble_diaz_level_candidates(max_level=5)
    scores = rank_candidates(candidates)

    assert "research-priority" in candidate_generation_markdown(candidates, scores)
    assert r"\begin{table}" in candidate_generation_latex(candidates, scores)
    hierarchy = coble_diaz_hierarchy_latex(candidates)
    assert "Level 3" in hierarchy
    assert "H^6" in hierarchy
