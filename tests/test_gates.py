"""Gate logic: suppression, geography, holds, warm routing, FIT floor."""

import csv
from pathlib import Path

import pytest

from caseinsight.gates import check_account

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def master():
    with open(DATA / "t100_master.csv", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture(scope="module")
def suppressed():
    with open(DATA / "suppression_list.csv", encoding="utf-8") as fh:
        return {r["account"] for r in csv.DictReader(fh)}


def _base_row(**overrides):
    row = {
        "company": "Acme Consumer Brands",
        "fit_score": "72",
        "tier": "Tier 2 Priority",
        "hq": "NY, US",
        "hold": "False",
    }
    row.update(overrides)
    return row


def test_no_t100_account_is_a_suppressed_client(master, suppressed):
    # The list was built excluding clients, pipeline, and references.
    for row in master:
        result = check_account(row, suppressed)
        assert "on the suppression list" not in result.reasons, row["company"]


def test_only_nurture_tier_blocks_on_the_t100(master, suppressed):
    blocked = [r["company"] for r in master
               if not check_account(r, suppressed).eligible]
    assert blocked == ["Faherty Brand"]


def test_conflict_holds_require_review(master, suppressed):
    holds = {r["company"] for r in master if r["hold"] == "True"}
    assert holds == {
        "Choice Hotels International", "Wyndham Hotels & Resorts",
        "Hyatt Hotels", "GoTo Foods", "Wingstop",
    }
    for row in master:
        if row["company"] in holds:
            result = check_account(row, suppressed)
            assert result.requires_review
            assert result.eligible  # flagged, not removed — clear with Sam


def test_suppression_matches_exact_names_not_substrings(suppressed):
    # "Ro" must not match "...roster"; slash-composites must match each part.
    assert check_account(_base_row(company="Ro"), suppressed).eligible
    assert not check_account(_base_row(company="Walmart"), suppressed).eligible
    assert not check_account(_base_row(company="Sam's Club"), suppressed).eligible
    assert not check_account(_base_row(company="LVMH"), suppressed).eligible


def test_fit_floor_blocks_sequences():
    result = check_account(_base_row(fit_score="44", tier="Disqualify"), set())
    assert not result.eligible


def test_germany_france_blocked_canada_flagged():
    assert not check_account(_base_row(hq="Munich, Germany"), set()).eligible
    assert not check_account(_base_row(hq="Paris, France"), set()).eligible
    canada = check_account(_base_row(hq="ON, Canada"), set())
    assert canada.eligible and canada.requires_review


def test_casl_flagged_accounts_require_review(master, suppressed):
    for name in ("Savers Value Village", "Bausch + Lomb"):
        row = next(r for r in master if r["company"] == name)
        assert check_account(row, suppressed).requires_review, name


def test_warm_relationship_routes_out_of_cold():
    result = check_account(_base_row(relationship_score="15"), set())
    assert not result.eligible
    assert any("HubSpot warm" in reason for reason in result.reasons)
