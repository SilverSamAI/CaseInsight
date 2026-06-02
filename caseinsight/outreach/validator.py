from __future__ import annotations
from ..models import EmailDraft
from ..facts.guardrail import check_output_for_violations, check_for_unapproved_claims


def validate_draft(draft: EmailDraft, facts: dict) -> EmailDraft:
    full_text = f"{draft.subject}\n{draft.body}"
    violations = check_output_for_violations(full_text, facts)
    suspicions = check_for_unapproved_claims(full_text, facts)
    draft.violations = violations + [f"[suspected] {s}" for s in suspicions]
    draft.passed_guardrail = len(violations) == 0
    return draft
