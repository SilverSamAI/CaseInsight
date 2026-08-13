"""Claim gate: approved metrics, reference discipline, banned phrases."""

from pathlib import Path

import pytest

from caseinsight.claims import verify_file, verify_text

SEQUENCES = sorted((Path(__file__).resolve().parent.parent / "sequences").glob("*.md"))


def test_sequences_exist():
    assert len(SEQUENCES) == 5


@pytest.mark.parametrize("path", SEQUENCES, ids=lambda p: p.stem)
def test_every_sequence_passes_the_claim_gate(path):
    violations = verify_file(path)
    assert not violations, "\n".join(str(v) for v in violations)


def test_approved_metrics_pass():
    assert verify_text(
        "Cost per asset came down 68 percent with output up. "
        "That is a 87.5 percent time reduction, 20x content volume, "
        "and 7 billion impressions under brand governance."
    ) == []


def test_unapproved_percentage_fails():
    assert any(v.kind == "unapproved-metric"
               for v in verify_text("We cut costs by 45 percent last year."))


def test_unapproved_multiplier_fails():
    assert any(v.kind == "unapproved-metric"
               for v in verify_text("Teams ship 10x more creative with us."))


def test_unapproved_impressions_fails():
    assert any(v.kind == "unapproved-metric"
               for v in verify_text("We delivered 3 billion impressions."))


def test_banned_phrases_fail():
    violations = verify_text("Hope this finds you well — just checking in.")
    kinds = {v.kind for v in violations}
    assert kinds == {"banned-phrase"}
    assert len(violations) == 2


def test_boilerplate_clients_fail_in_cold_copy():
    assert any(v.kind == "unapproved-reference"
               for v in verify_text("We work with Adobe and Fifth Third Bank."))
    assert any(v.kind == "unapproved-reference"
               for v in verify_text("Our client Smoothie King saw results."))


def test_approved_references_pass():
    assert verify_text("Sam's Club, Coca-Cola, Marc Jacobs, and BMW trust the system.") == []


def test_prospect_arithmetic_is_not_a_claim():
    assert verify_text(
        "Forty shades times six channels times four markets is 960 assets. "
        "A seven figure campaign shipped with three versions, and a type "
        "change cost $8,000."
    ) == []
