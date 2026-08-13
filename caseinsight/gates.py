"""Outbound eligibility gates — Playbook Sections 14, 16.5, 18.1, 18.2.

FIT is the gate, INTENT is the timer. These checks decide whether an
account may enter a cold sequence at all; nothing here sends anything.
Human-in-the-loop approval before any send is a standing instruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FIT_FLOOR = 45                 # below this an account never enters a sequence
WARM_RELATIONSHIP_FLOOR = 15   # at/above this, route to HubSpot warm, never cold

# No direct cold sequences into these countries (Section 18.1, item 8).
BLOCKED_COUNTRIES = {"Germany", "France"}
CASL_REVIEW_COUNTRIES = {"Canada"}

# Accounts the Method tab flags for CASL review before any send.
CASL_FLAGGED_ACCOUNTS = {"Savers Value Village", "Bausch + Lomb"}


@dataclass
class GateResult:
    eligible: bool
    requires_review: bool = False
    reasons: list[str] = field(default_factory=list)


def _norm(name: str) -> str:
    return " ".join(name.lower().replace("&", "and").split())


def check_account(row: dict, suppressed_accounts: set[str]) -> GateResult:
    """Evaluate one t100_master row against every pre-sequence account gate.

    ``row`` uses the canonical data/t100_master.csv column names.
    ``suppressed_accounts`` holds names from data/suppression_list.csv.
    """
    reasons: list[str] = []
    review: list[str] = []

    fit = int(float(row["fit_score"]))
    if fit < FIT_FLOOR:
        reasons.append(f"fit_score {fit} below floor {FIT_FLOOR}")

    tier = row["tier"]
    if tier == "Disqualify":
        reasons.append("tier is Disqualify")
    if tier == "Nurture":
        reasons.append("tier is Nurture: content and events only, no sequence")

    # Suppression entries can name several entities ("Sam's Club / Walmart");
    # match each exactly after normalization — substring matching false-hits
    # short names like "Ro".
    company = _norm(row["company"])
    suppressed_names = {
        _norm(part) for s in suppressed_accounts for part in s.split("/")
    }
    if company in suppressed_names:
        reasons.append("on the suppression list")

    hq = row.get("hq", "")
    for country in BLOCKED_COUNTRIES:
        if country.lower() in hq.lower():
            reasons.append(f"HQ in {country}: partner-led via Serviceplan only")
    for country in CASL_REVIEW_COUNTRIES:
        if country.lower() in hq.lower():
            review.append(f"HQ footprint in {country}: CASL legal review before any send")
    if row["company"] in CASL_FLAGGED_ACCOUNTS:
        review.append("CASL review flagged on the Method tab")

    if str(row.get("hold", "")).lower() in ("true", "1"):
        review.append("HOLD: conflict check must be cleared with Sam before outreach")

    relationship = row.get("relationship_score")
    if relationship not in (None, "") and float(relationship) >= WARM_RELATIONSHIP_FLOOR:
        reasons.append("relationship_score >= 15: route to HubSpot warm, never cold")

    return GateResult(
        eligible=not reasons,
        requires_review=bool(review),
        reasons=reasons + review,
    )


# Pre-sequence contact rules (Sections 17.2, 24.12) for list builds.
CONTACT_SCORE_FLOOR = 24
MIN_CONTACTS_PER_ACCOUNT = 2
MAX_CONTACTS_PER_ACCOUNT = 8
NEVER_SEQUENCE_DEPARTMENTS = {"Legal", "Finance", "Human Resources", "Information Security"}
