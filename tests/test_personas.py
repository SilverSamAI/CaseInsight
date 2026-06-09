from caseinsight.personas import infer_persona, get_best_proof_points

FACTS = {
    "clients": [],
    "metrics": [],
    "proof_points": [
        {
            "id": "coke_holiday",
            "text": "Coca-Cola campaign proof.",
            "usage": "approved_for_outbound",
            "best_for_personas": ["CMO", "VP Brand", "Chief Brand Officer", "VP Creative"],
        },
        {
            "id": "svedka",
            "text": "Svedka Super Bowl proof.",
            "usage": "approved_for_outbound",
            "best_for_personas": ["CMO", "VP Marketing", "Chief Growth Officer", "VP Brand"],
        },
        {
            "id": "system_not_asset",
            "text": "System not asset proof.",
            "usage": "approved_for_outbound",
            "best_for_personas": ["all"],
        },
    ],
    "offerings": {},
}


def test_cmo_inferred():
    assert infer_persona("Chief Marketing Officer") == "CMO"


def test_vp_marketing_inferred():
    assert infer_persona("VP of Marketing") == "VP Marketing"


def test_creative_director_inferred():
    assert infer_persona("Creative Director, EMEA") == "VP Creative"


def test_unknown_falls_back():
    assert infer_persona("Accountant") == "all"


def test_none_falls_back():
    assert infer_persona(None) == "all"


def test_cmo_gets_relevant_proof_points():
    results = get_best_proof_points(FACTS, "CMO")
    texts = [r["text"] for r in results]
    assert any("Coca-Cola" in t for t in texts)
    assert any("Svedka" in t for t in texts)
    assert any("System not asset" in t for t in texts)


def test_unknown_persona_gets_all_proofs():
    results = get_best_proof_points(FACTS, "all")
    assert len(results) == 1  # only "all" tagged proof
