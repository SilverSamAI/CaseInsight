"""ICP FIT scoring rubric — Playbook Section 16.1, 100 points across 14 categories.

Each ``score_*`` function maps a raw observable to rubric points, so a
net-new account can be scored from enrichment data, and an existing row
can be rescored when a placeholder input (AI maturity, tech signature)
is replaced by a verified one.

Constraint carried from the workbook Method tab: AI maturity defaults to
stage "unverified" (5 points) and tech signature to 2 points on every
unenriched row. Treat any FIT built on those defaults as a floor.
"""

from __future__ import annotations

from dataclasses import dataclass

# Score-component column names in data/t100_master.csv, in rubric order.
SCORE_COLUMNS = [
    "score_industry",      # /12
    "score_revenue",       # /10
    "score_employees",     # /4
    "score_spend",         # /8
    "score_volume",        # /10
    "score_video",         # /6
    "score_brands",        # /8
    "score_markets",       # /7
    "score_locations",     # /5
    "score_sku",           # /6
    "score_media",         # /6
    "score_ai",            # /8
    "score_tech",          # /5
    "score_procurement",   # /5
]

MAX_POINTS = {
    "score_industry": 12,
    "score_revenue": 10,
    "score_employees": 4,
    "score_spend": 8,
    "score_volume": 10,
    "score_video": 6,
    "score_brands": 8,
    "score_markets": 7,
    "score_locations": 5,
    "score_sku": 6,
    "score_media": 6,
    "score_ai": 8,
    "score_tech": 5,
    "score_procurement": 5,
}

# Unverified placeholder values used on every row of the source list.
AI_UNVERIFIED_DEFAULT = 5
TECH_UNVERIFIED_DEFAULT = 2

# Industry tier -> points (Section 16.1 row 1). Tier 4 is a hard disqualify.
INDUSTRY_TIER_POINTS = {1: 12, 2: 8, 3: 4, 4: 0}

# Playbook Section 3.1 taxonomy, restricted to verticals present on the T100.
VERTICAL_TIER = {
    "Omnichannel retail": 1,
    "CPG multi brand": 1,
    "Beauty and personal care": 1,
    "Fashion and apparel": 1,
    "Fashion and footwear": 1,
    "Fashion and accessories": 1,
    "QSR and fast casual": 1,
    "QSR and franchise": 1,
    "Consumer health and wellness": 2,
    "Consumer health and device": 2,
    "Hospitality": 2,
    "Hospitality and franchise": 2,
    "Consumer electronics": 2,
    "Consumer electronics and appliances": 2,
    "Automotive": 2,
    "Automotive and powersports": 2,
    "Multi unit franchise services": 2,
}


def score_industry(tier: int) -> int:
    """Industry fit /12. Tier 4 scores 0 AND hard-disqualifies (see gates)."""
    return INDUSTRY_TIER_POINTS[tier]


def score_revenue(revenue_band: str, has_sponsor: bool = False) -> int:
    """Annual revenue /10."""
    table = {
        "$1B to $5B": 10,
        "$500M to $1B": 9,
        "$250M to $500M": 8,
        "$5B to $10B": 8,
        "$100M to $250M": 5,
    }
    if revenue_band == "Over $10B":
        return 9 if has_sponsor else 5
    if revenue_band == "Under $100M":
        return 0
    return table[revenue_band]


def score_employees(count: int) -> int:
    """Employee count /4 — a procurement-complexity proxy, not a fit signal."""
    if count < 50:
        return 0
    if count <= 200:
        return 1
    if count <= 500:
        return 3
    if count <= 1000:
        return 4
    if count <= 5000:
        return 4
    if count <= 10000:
        return 3
    return 2


def score_marketing_spend(annual_usd: float) -> int:
    """Marketing spend /8, from EDGAR advertising expense or ad-library proxy."""
    m = annual_usd / 1_000_000
    if m >= 50:
        return 8
    if m >= 20:
        return 7
    if m >= 10:
        return 5
    if m >= 5:
        return 4
    if m >= 1:
        return 2
    return 0


def score_content_volume(assets_per_month: int) -> int:
    """Content volume /10."""
    if assets_per_month >= 500:
        return 10
    if assets_per_month >= 200:
        return 8
    if assets_per_month >= 100:
        return 6
    if assets_per_month >= 50:
        return 3
    return 0


def score_video_need(cadence: str) -> int:
    """Video production need /6: continuous | campaign | occasional | none."""
    return {"continuous": 6, "campaign": 4, "occasional": 2, "none": 0}[cadence]


def score_brands(count: int) -> int:
    """Number of brands /8."""
    if count >= 10:
        return 8
    if count >= 5:
        return 7
    if count >= 3:
        return 5
    if count == 2:
        return 3
    return 1


def score_markets(count: int) -> int:
    """Markets or languages /7."""
    if count >= 10:
        return 7
    if count >= 5:
        return 6
    if count >= 3:
        return 4
    if count == 2:
        return 2
    return 0


def score_locations(count: int) -> int:
    """Locations or franchise count /5. Non-applicable scores 0."""
    if count >= 500:
        return 5
    if count >= 100:
        return 4
    if count >= 25:
        return 2
    return 0


def score_sku(sku_count: int, strong_ecomm: bool = True) -> int:
    """E-commerce maturity and SKU count /6."""
    if sku_count >= 5000 and strong_ecomm:
        return 6
    if sku_count >= 1000:
        return 5
    if sku_count >= 500:
        return 3
    if sku_count >= 100:
        return 2
    return 0


def score_paid_media(active_meta_creatives: int) -> int:
    """Paid media activity /6, from Meta Ad Library active creative count."""
    if active_meta_creatives >= 200:
        return 6
    if active_meta_creatives >= 100:
        return 5
    if active_meta_creatives >= 50:
        return 3
    if active_meta_creatives >= 10:
        return 1
    return 0


def score_ai_stage(stage: int | None) -> int:
    """AI readiness stage /8 (Playbook Section 12). None = unverified default."""
    if stage is None:
        return AI_UNVERIFIED_DEFAULT
    return {1: 0, 2: 3, 3: 7, 4: 8, 5: 8, 6: 7, 7: 4, 8: 1}[stage]


def score_tech_signature(systems_detected: int | None) -> int:
    """Technology signature /5: enterprise DAM + PIM + gen-AI seats.

    3 detected = 5, 2 = 4, 1 = 2, 0 = 0. None = unverified default.
    """
    if systems_detected is None:
        return TECH_UNVERIFIED_DEFAULT
    return {3: 5, 2: 4, 1: 2, 0: 0}[systems_detected]


def score_procurement(revenue_band: str, heavily_regulated: bool = False) -> int:
    """Procurement feasibility /5, inferred from firmographics."""
    if heavily_regulated:
        return 0
    if revenue_band == "Over $10B":
        return 1
    if revenue_band in ("$1B to $5B", "$5B to $10B"):
        return 3
    return 5


def fit_score(components: dict) -> int:
    """Total FIT /100: sum of the 14 component scores."""
    for col in SCORE_COLUMNS:
        value = int(components[col])
        if not 0 <= value <= MAX_POINTS[col]:
            raise ValueError(f"{col}={value} outside 0..{MAX_POINTS[col]}")
    return sum(int(components[col]) for col in SCORE_COLUMNS)


# FIT-only tier thresholds used by the T100 workbook (Scoring Rubric tab).
# The blended TOTAL PRIORITY tiering in Section 16.5 uses different bands
# and requires INTENT / RELATIONSHIP / OPPORTUNITY, which are computed
# outside this repo (CLAW/SAGE Postgres) and are unreliable until OAuth
# reply tracking is live.
@dataclass(frozen=True)
class Tier:
    name: str
    floor: int
    contacts: str
    research: str
    sequence: str


TIERS = [
    Tier("Tier 1 Named", 78, "5 to 8", "60 to 90 min per account", "Fully bespoke, hand written"),
    Tier("Tier 2 Priority", 68, "4 to 6", "20 to 30 min per account", "Vertical template plus 2 personalized lines per email"),
    Tier("Tier 3 Volume", 58, "2 to 3", "Zero. Do not research", "Vertical template plus 1 merge personalized line"),
    Tier("Nurture", 45, "1", "Zero", "Content and event only. No sequence"),
    Tier("Disqualify", 0, "0", "Zero", "Suppress. Log disqualification_reason"),
]

# Contact targets per tier for Apollo list builds (midpoint planning numbers).
CONTACTS_PER_ACCOUNT = {
    "Tier 1 Named": 6,
    "Tier 2 Priority": 5,
    "Tier 3 Volume": 3,
    "Nurture": 1,
    "Disqualify": 0,
}


def tier_for_fit(fit: int) -> str:
    for tier in TIERS:
        if fit >= tier.floor:
            return tier.name
    return "Disqualify"


def rescore(components: dict, ai_stage: int | None = None,
            tech_systems_detected: int | None = None) -> dict:
    """Rescore a row after enrichment replaces the unverified defaults.

    Returns a new components dict plus recomputed ``fit_score`` and ``tier``.
    Enriching AI maturity and tech signature typically moves FIT by +5 to
    +11 points, which can promote an account by a full tier.
    """
    updated = dict(components)
    if ai_stage is not None:
        updated["score_ai"] = score_ai_stage(ai_stage)
    if tech_systems_detected is not None:
        updated["score_tech"] = score_tech_signature(tech_systems_detected)
    fit = fit_score(updated)
    return {**updated, "fit_score": fit, "tier": tier_for_fit(fit)}
