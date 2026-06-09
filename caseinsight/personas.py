from __future__ import annotations

PERSONA_KEYWORDS: dict[str, list[str]] = {
    "CMO": ["chief marketing", "cmo"],
    "VP Marketing": ["vp marketing", "vice president marketing", "vp of marketing"],
    "VP Brand": ["vp brand", "vice president brand", "head of brand", "brand director"],
    "Chief Brand Officer": ["chief brand"],
    "VP Creative": ["vp creative", "vice president creative", "head of creative", "creative director"],
    "Chief Growth Officer": ["chief growth", "cgo", "head of growth"],
    "Chief Digital Officer": ["chief digital", "cdo"],
    "VP Content": ["vp content", "head of content", "director of content"],
    "Head of Creative Operations": ["creative ops", "head of creative operations", "director of creative operations"],
    "Innovation Lead": ["innovation", "head of innovation", "director of innovation"],
}


def infer_persona(title: str | None) -> str:
    """Map a free-form job title to one of the persona buckets used in silverside_facts.yaml."""
    if not title:
        return "all"
    t = title.lower()
    for persona, keywords in PERSONA_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return persona
    return "all"


def get_best_proof_points(facts: dict, persona: str) -> list[dict]:
    """Return proof points that match a persona, falling back to 'all' proofs."""
    from .facts.loader import get_approved_proof_points

    approved = get_approved_proof_points(facts)
    matched = [
        p for p in approved
        if persona in p.get("best_for_personas", []) or "all" in p.get("best_for_personas", [])
    ]
    return matched if matched else approved
