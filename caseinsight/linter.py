from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LintError:
    level: str  # "error" | "warning"
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.path}: {self.message}"


def lint_facts(facts: dict) -> list[LintError]:
    """Validate silverside_facts.yaml for structural and flag correctness."""
    errors: list[LintError] = []

    # ── company ──────────────────────────────────────────────────────────────
    company = facts.get("company", {})
    for field in ("positioning_line", "network_claim"):
        block = company.get(field, {})
        if not block.get("text"):
            errors.append(LintError("error", f"company.{field}", "missing 'text' key"))
        if block.get("usage") != "approved_for_outbound":
            errors.append(LintError("warning", f"company.{field}", "usage is not approved_for_outbound"))

    # ── clients ───────────────────────────────────────────────────────────────
    valid_outbound = {"approved", "needs_verification"}
    for i, client in enumerate(facts.get("clients", [])):
        ref = f"clients[{i}] ({client.get('name', '?')})"
        if not client.get("name"):
            errors.append(LintError("error", ref, "missing 'name'"))
        if client.get("outbound_use") not in valid_outbound:
            errors.append(LintError("error", ref, f"outbound_use must be one of {valid_outbound}"))

    # ── metrics ───────────────────────────────────────────────────────────────
    valid_usage = {"approved_for_outbound", "needs_verification"}
    for i, metric in enumerate(facts.get("metrics", [])):
        ref = f"metrics[{i}] ({metric.get('id', '?')})"
        if not metric.get("value"):
            errors.append(LintError("error", ref, "missing 'value'"))
        if not metric.get("label"):
            errors.append(LintError("error", ref, "missing 'label'"))
        if metric.get("usage") not in valid_usage:
            errors.append(LintError("error", ref, f"usage must be one of {valid_usage}"))

    # ── proof points ──────────────────────────────────────────────────────────
    for i, pp in enumerate(facts.get("proof_points", [])):
        ref = f"proof_points[{i}] ({pp.get('id', '?')})"
        if not pp.get("text"):
            errors.append(LintError("error", ref, "missing 'text'"))
        if pp.get("usage") not in valid_usage:
            errors.append(LintError("error", ref, f"usage must be one of {valid_usage}"))
        if not pp.get("best_for_personas"):
            errors.append(LintError("warning", ref, "no best_for_personas — will apply to all"))

    # ── offerings ─────────────────────────────────────────────────────────────
    for key, offering in facts.get("offerings", {}).items():
        if isinstance(offering, dict):
            if not offering.get("name"):
                errors.append(LintError("warning", f"offerings.{key}", "missing 'name'"))
            if not offering.get("one_liner"):
                errors.append(LintError("warning", f"offerings.{key}", "missing 'one_liner'"))

    # ── positioning lists ─────────────────────────────────────────────────────
    if not facts.get("position_as"):
        errors.append(LintError("error", "position_as", "list is empty"))
    if not facts.get("do_not_position_as"):
        errors.append(LintError("warning", "do_not_position_as", "list is empty"))
    if not facts.get("forbidden_in_copy"):
        errors.append(LintError("warning", "forbidden_in_copy", "list is empty — no terms will be blocked"))

    # ── cross-check: proof point proof_default in offerings ───────────────────
    offering_proof_ids = {
        o.get("proof_default")
        for o in facts.get("offerings", {}).values()
        if isinstance(o, dict)
    }
    proof_point_ids = {p.get("id") for p in facts.get("proof_points", [])}
    for oid in offering_proof_ids:
        if oid and oid not in proof_point_ids:
            errors.append(LintError("warning", "offerings.proof_default", f"references unknown proof_point id '{oid}'"))

    return errors
