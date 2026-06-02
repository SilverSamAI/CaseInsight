from __future__ import annotations
import re
from .loader import (
    get_approved_clients,
    get_unapproved_clients,
    get_approved_metrics,
    get_approved_proof_points,
)


def build_approved_facts_block(facts: dict) -> str:
    lines = ["APPROVED FACTS (use only these - never invent claims):"]
    idx = 1

    company = facts.get("company", {})
    if pl := company.get("positioning_line", {}).get("text"):
        lines.append(f"[{idx}] positioning: \"{pl}\"")
        idx += 1
    if nc := company.get("network_claim", {}).get("text"):
        lines.append(f"[{idx}] network: \"{nc}\"")
        idx += 1

    for client in get_approved_clients(facts):
        lines.append(f"[{idx}] client: {client}")
        idx += 1

    for m in get_approved_metrics(facts):
        lines.append(f"[{idx}] metric: \"{m['value']} {m['label']}\"")
        if guidance := m.get("guidance"):
            lines.append(f"       (note: {guidance})")
        idx += 1

    for p in get_approved_proof_points(facts):
        lines.append(f"[{idx}] proof: \"{p['text']}\"")
        idx += 1

    return "\n".join(lines)


def build_offerings_block(facts: dict) -> str:
    lines = []
    for offering in facts.get("offerings", {}).values():
        if isinstance(offering, dict):
            name = offering.get("name", "")
            one_liner = offering.get("one_liner", "")
            if name:
                lines.append(f"- {name}: {one_liner}")
    return "\n".join(lines)


def check_output_for_violations(text: str, facts: dict) -> list[str]:
    violations = []
    text_lower = text.lower()

    for term in facts.get("forbidden_in_copy", []):
        if term.lower() in text_lower:
            violations.append(f"Forbidden term found: '{term}'")

    for client in get_unapproved_clients(facts):
        if client.lower() in text_lower:
            violations.append(f"Unapproved client name found: '{client}'")

    if "—" in text:
        violations.append("Em dash found (forbidden by style rules)")

    return violations


def check_for_unapproved_claims(text: str, facts: dict) -> list[str]:
    approved_values = {m["value"] for m in get_approved_metrics(facts)}
    suspicions = []
    for match in re.finditer(r'(\d+(?:\.\d+)?\s?[x%])', text):
        num = match.group(1).replace(" ", "")
        if not any(num in v.replace(" ", "") for v in approved_values):
            suspicions.append(f"Unverified numeric claim: '{num}'")
    return suspicions
