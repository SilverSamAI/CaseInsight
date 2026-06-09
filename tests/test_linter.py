import copy
import pytest
from caseinsight.linter import lint_facts

VALID_FACTS = {
    "company": {
        "positioning_line": {"text": "An AI lab.", "usage": "approved_for_outbound"},
        "network_claim": {"text": "30+ offices.", "usage": "approved_for_outbound"},
    },
    "clients": [
        {"name": "Acme", "outbound_use": "approved"},
    ],
    "metrics": [
        {"id": "cost", "value": "68%", "label": "Cost Reduction", "usage": "approved_for_outbound"},
    ],
    "proof_points": [
        {
            "id": "p1",
            "text": "We did a thing.",
            "usage": "approved_for_outbound",
            "best_for_personas": ["all"],
        },
    ],
    "offerings": {
        "ai_video": {"name": "AI Video", "one_liner": "Great video.", "proof_default": "p1"},
    },
    "position_as": ["AI lab"],
    "do_not_position_as": ["generic tool"],
    "forbidden_in_copy": ["guarantee"],
}


def test_valid_facts_no_errors():
    errors = lint_facts(VALID_FACTS)
    assert errors == []


def test_missing_client_name():
    facts = copy.deepcopy(VALID_FACTS)
    facts["clients"].append({"outbound_use": "approved"})
    errors = lint_facts(facts)
    assert any("missing 'name'" in e.message for e in errors)


def test_invalid_outbound_use():
    facts = copy.deepcopy(VALID_FACTS)
    facts["clients"][0]["outbound_use"] = "unknown_value"
    errors = lint_facts(facts)
    assert any("outbound_use" in e.message for e in errors)


def test_missing_metric_value():
    facts = copy.deepcopy(VALID_FACTS)
    facts["metrics"][0].pop("value")
    errors = lint_facts(facts)
    assert any("missing 'value'" in e.message for e in errors)


def test_invalid_proof_default_warns():
    facts = copy.deepcopy(VALID_FACTS)
    facts["offerings"]["ai_video"]["proof_default"] = "nonexistent_id"
    errors = lint_facts(facts)
    assert any("nonexistent_id" in e.message for e in errors)


def test_empty_position_as_errors():
    facts = copy.deepcopy(VALID_FACTS)
    facts["position_as"] = []
    errors = lint_facts(facts)
    assert any(e.level == "error" and "position_as" in e.path for e in errors)


def test_real_facts_file_passes():
    from caseinsight.facts.loader import load_facts
    facts = load_facts("silverside_facts.yaml")
    errors = lint_facts(facts)
    hard_errors = [e for e in errors if e.level == "error"]
    assert hard_errors == [], [str(e) for e in hard_errors]
