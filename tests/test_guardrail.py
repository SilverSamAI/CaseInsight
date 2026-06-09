import pytest
from caseinsight.facts.guardrail import check_output_for_violations, check_for_unapproved_claims

SAMPLE_FACTS = {
    "company": {
        "positioning_line": {"text": "An AI innovation lab", "usage": "approved_for_outbound"},
        "network_claim": {"text": "30+ offices", "usage": "approved_for_outbound"},
    },
    "clients": [
        {"name": "Coca-Cola", "outbound_use": "approved"},
        {"name": "Google Fiber", "outbound_use": "needs_verification"},
    ],
    "metrics": [
        {"id": "cost", "value": "68%", "label": "Cost Reduction", "usage": "approved_for_outbound"},
    ],
    "proof_points": [
        {"id": "coke", "text": "We helped Coca-Cola", "usage": "approved_for_outbound"},
    ],
    "offerings": {},
    "position_as": ["AI-native creative innovation lab"],
    "do_not_position_as": ["A generic AI tool"],
    "forbidden_in_copy": ["guarantee"],
}


def test_clean_text_passes():
    assert check_output_for_violations("We work with Coca-Cola on AI campaigns.", SAMPLE_FACTS) == []


def test_forbidden_term_caught():
    violations = check_output_for_violations("We guarantee results.", SAMPLE_FACTS)
    assert any("guarantee" in v.lower() for v in violations)


def test_unapproved_client_caught():
    violations = check_output_for_violations("We worked with Google Fiber.", SAMPLE_FACTS)
    assert any("Google Fiber" in v for v in violations)


def test_em_dash_caught():
    violations = check_output_for_violations("Great work — see you soon.", SAMPLE_FACTS)
    assert any("em dash" in v.lower() for v in violations)


def test_approved_metric_not_flagged():
    suspicions = check_for_unapproved_claims("We achieved 68% cost reduction.", SAMPLE_FACTS)
    assert not any("68%" in s for s in suspicions)


def test_unapproved_metric_flagged():
    suspicions = check_for_unapproved_claims("We deliver 99% accuracy.", SAMPLE_FACTS)
    assert any("99%" in s for s in suspicions)
