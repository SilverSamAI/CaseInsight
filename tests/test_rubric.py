"""Rubric integrity: every T100 row and the band functions match Section 16.1."""

import csv
from pathlib import Path

import pytest

from caseinsight import rubric

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def master():
    with open(DATA / "t100_master.csv", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_master_has_100_accounts(master):
    assert len(master) == 100


def test_fit_equals_component_sum_on_every_row(master):
    for row in master:
        assert rubric.fit_score(row) == int(row["fit_score"]), row["company"]


def test_tier_matches_fit_thresholds_on_every_row(master):
    for row in master:
        assert rubric.tier_for_fit(int(row["fit_score"])) == row["tier"], row["company"]


def test_component_scores_within_rubric_maxima(master):
    for row in master:
        for col, cap in rubric.MAX_POINTS.items():
            assert 0 <= int(row[col]) <= cap, (row["company"], col)


def test_ai_and_tech_are_unverified_defaults_everywhere(master):
    # Method tab: placeholders, not assessments. If this fails, enrichment
    # has landed and the summary caveat should be retired.
    assert all(int(r["score_ai"]) == rubric.AI_UNVERIFIED_DEFAULT for r in master)
    assert all(int(r["score_tech"]) == rubric.TECH_UNVERIFIED_DEFAULT for r in master)


def test_tier_thresholds():
    assert rubric.tier_for_fit(78) == "Tier 1 Named"
    assert rubric.tier_for_fit(77) == "Tier 2 Priority"
    assert rubric.tier_for_fit(68) == "Tier 2 Priority"
    assert rubric.tier_for_fit(67) == "Tier 3 Volume"
    assert rubric.tier_for_fit(58) == "Tier 3 Volume"
    assert rubric.tier_for_fit(57) == "Nurture"
    assert rubric.tier_for_fit(45) == "Nurture"
    assert rubric.tier_for_fit(44) == "Disqualify"


def test_revenue_band_scoring():
    assert rubric.score_revenue("$1B to $5B") == 10
    assert rubric.score_revenue("$500M to $1B") == 9
    assert rubric.score_revenue("$250M to $500M") == 8
    assert rubric.score_revenue("$5B to $10B") == 8
    assert rubric.score_revenue("$100M to $250M") == 5
    assert rubric.score_revenue("Over $10B") == 5
    assert rubric.score_revenue("Over $10B", has_sponsor=True) == 9
    assert rubric.score_revenue("Under $100M") == 0


def test_ai_stage_scoring_matches_section_12():
    assert rubric.score_ai_stage(4) == 8
    assert rubric.score_ai_stage(5) == 8
    assert rubric.score_ai_stage(3) == 7
    assert rubric.score_ai_stage(6) == 7
    assert rubric.score_ai_stage(7) == 4
    assert rubric.score_ai_stage(2) == 3
    assert rubric.score_ai_stage(8) == 1
    assert rubric.score_ai_stage(1) == 0
    assert rubric.score_ai_stage(None) == rubric.AI_UNVERIFIED_DEFAULT


def test_rescore_promotes_tier_when_enrichment_lands(master):
    # A 77-FIT Tier 2 account with a verified stage-4 AI program (+3) and a
    # full tech signature (+3) crosses the Tier 1 threshold.
    row = {c: int(next(r for r in master if r["fit_score"] == "77")[c])
           for c in rubric.SCORE_COLUMNS}
    result = rubric.rescore(row, ai_stage=4, tech_systems_detected=3)
    assert result["fit_score"] == 77 + 3 + 3
    assert result["tier"] == "Tier 1 Named"


def test_fit_score_rejects_out_of_range_components():
    bad = {c: 0 for c in rubric.SCORE_COLUMNS}
    bad["score_industry"] = 13
    with pytest.raises(ValueError):
        rubric.fit_score(bad)
