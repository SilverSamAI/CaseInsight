"""Build the canonical T100 dataset and all import artifacts from source files.

Usage:  python -m caseinsight.build

Reads   data/source/T100_Master_Enriched.xlsx   (enrichment, waves, holds, domains)
        data/source/Top100_Targets_Scored.csv   (14 rubric score components)
        data/source/Silverside_Top_100_Cold_Outbound_Targets.xlsx (suppression tab)

Writes  data/t100_master.csv          canonical merged dataset
        data/suppression_list.csv     do-not-cold-email accounts
        exports/apollo/*.csv          wave and vertical list uploads
        exports/hubspot/*.csv         company import mapped to portal properties
        exports/research/*.md         Wave 1 Tier 1/2 research queue
        exports/reports/*.md          program summary

Nothing here writes to Apollo or HubSpot. Imports are staged as files and
require human review — human-in-the-loop approval is a standing instruction.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import openpyxl

from .gates import check_account
from .rubric import (
    CONTACTS_PER_ACCOUNT,
    SCORE_COLUMNS,
    VERTICAL_TIER,
    fit_score,
    tier_for_fit,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SOURCE = DATA / "source"
EXPORTS = ROOT / "exports"

# Raw score column headers in the source CSV, in rubric order.
RAW_SCORE_HEADERS = [
    "Ind /12", "Rev /10", "Emp /4", "Spend /8", "Vol /10", "Vid /6",
    "Brands /8", "Mkts /7", "Locs /5", "SKU /6", "Media /6", "AI /8",
    "Tech /5", "Proc /5",
]

# Canonical column order for data/t100_master.csv.
MASTER_COLUMNS = [
    "rank", "company", "primary_domain", "alt_domain", "domain_confidence",
    "in_hubspot", "hs_matched_domain", "hs_lifecycle",
    "vertical", "vertical_group", "industry_tier", "segments",
    "revenue_band", "hq", "ownership",
    "tier", "wave", "fit_score", "hold",
    "outbound_eligible", "requires_review", "gate_notes",
    *SCORE_COLUMNS,
    "primary_multiplier", "fit_rationale", "primary_use_case",
    "est_first_deal", "target_titles", "trigger_hypothesis",
    "verification_required", "reference_to_cite", "notes", "apollo_lists",
]

ENRICHED_TO_MASTER = {
    "Rank": "rank",
    "Company": "company",
    "Primary Domain": "primary_domain",
    "Alt Domain": "alt_domain",
    "Domain Confidence": "domain_confidence",
    "In HubSpot": "in_hubspot",
    "HS Matched Domain": "hs_matched_domain",
    "HS Lifecycle": "hs_lifecycle",
    "Vertical": "vertical",
    "Vertical Group": "vertical_group",
    "Segment": "segments",
    "Est. Revenue Band": "revenue_band",
    "HQ": "hq",
    "Ownership": "ownership",
    "TIER": "tier",
    "Wave": "wave",
    "FIT SCORE": "fit_score",
    "Hold": "hold",
    "Primary Multiplier [FACT]": "primary_multiplier",
    "Fit Rationale [INFERENCE]": "fit_rationale",
    "Primary Use Case": "primary_use_case",
    "Est. First Deal": "est_first_deal",
    "Target Titles": "target_titles",
    "Trigger Hypothesis [VERIFY]": "trigger_hypothesis",
    "Verification Required Before Send": "verification_required",
    "Reference to Cite": "reference_to_cite",
    "Notes / Conflict Check": "notes",
    "Apollo Lists": "apollo_lists",
}


def _read_enriched() -> list[dict]:
    wb = openpyxl.load_workbook(
        SOURCE / "T100_Master_Enriched.xlsx", read_only=True, data_only=True
    )
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    header = list(rows[0])
    out = []
    for raw in rows[1:]:
        if raw[0] is None:
            continue
        rec = dict(zip(header, raw))
        out.append({dst: rec.get(src) for src, dst in ENRICHED_TO_MASTER.items()})
    return out


def _read_scores() -> dict[str, dict]:
    with open(SOURCE / "Top100_Targets_Scored.csv", encoding="utf-8") as fh:
        raw = list(csv.reader(fh))
    header = raw[3]
    scores: dict[str, dict] = {}
    for row in raw[4:]:
        if not (row and row[0].strip() and row[0].strip().replace(".", "").isdigit()):
            continue
        rec = dict(zip(header, row))
        scores[rec["Company"]] = {
            dst: int(rec[src]) for src, dst in zip(RAW_SCORE_HEADERS, SCORE_COLUMNS)
        }
    return scores


def _read_suppression() -> list[dict]:
    wb = openpyxl.load_workbook(
        SOURCE / "Silverside_Top_100_Cold_Outbound_Targets.xlsx",
        read_only=True, data_only=True,
    )
    ws = wb["Suppression List"]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    wb.close()
    out = []
    header_seen = False
    for row in rows:
        cells = [c for c in row if c not in (None, "")]
        if not cells:
            continue
        if row[0] == "Account":
            header_seen = True
            continue
        if not header_seen or len(cells) < 3 or str(row[0]).startswith("ACTION"):
            continue
        out.append({
            "account": row[0], "status": row[1], "vertical": row[2],
            "route": row[3], "note": row[4],
        })
    return out


def build_master() -> tuple[list[dict], list[dict]]:
    accounts = _read_enriched()
    scores = _read_scores()
    suppression = _read_suppression()
    suppressed_names = {s["account"] for s in suppression}

    for acct in accounts:
        acct.update(scores[acct["company"]])

        # Integrity: stored FIT must equal the component sum, and the stored
        # tier must match the FIT thresholds.
        computed = fit_score(acct)
        stored = int(float(acct["fit_score"]))
        if computed != stored:
            raise ValueError(f"{acct['company']}: stored FIT {stored} != computed {computed}")
        acct["fit_score"] = stored
        expected_tier = tier_for_fit(stored)
        if acct["tier"] != expected_tier:
            raise ValueError(f"{acct['company']}: tier {acct['tier']} != expected {expected_tier}")

        acct["industry_tier"] = f"Tier {VERTICAL_TIER[acct['vertical']]}"
        acct["rank"] = int(float(acct["rank"]))
        acct["wave"] = int(float(acct["wave"]))
        acct["in_hubspot"] = bool(acct["in_hubspot"])
        acct["hold"] = bool(acct["hold"])

        gate = check_account(
            {k: ("" if v is None else v) for k, v in acct.items()}, suppressed_names
        )
        acct["outbound_eligible"] = gate.eligible
        acct["requires_review"] = gate.requires_review
        acct["gate_notes"] = "; ".join(gate.reasons)

    accounts.sort(key=lambda a: a["rank"])
    return accounts, suppression


def write_master(accounts: list[dict], suppression: list[dict]) -> None:
    with open(DATA / "t100_master.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=MASTER_COLUMNS)
        writer.writeheader()
        for acct in accounts:
            writer.writerow({k: acct.get(k, "") for k in MASTER_COLUMNS})

    with open(DATA / "suppression_list.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["account", "status", "vertical", "route", "note"])
        writer.writeheader()
        writer.writerows(suppression)


def write_apollo_exports(accounts: list[dict], suppression: list[dict]) -> None:
    """Apollo account uploads: one file per wave, one master, one suppression."""
    out = EXPORTS / "apollo"
    out.mkdir(parents=True, exist_ok=True)
    fields = [
        "company", "primary_domain", "vertical_group", "tier", "wave",
        "fit_score", "contacts_target", "apollo_lists", "hold", "gate_notes",
    ]

    def _rows(subset):
        for acct in subset:
            yield {
                **{k: acct[k] for k in fields if k in acct},
                "contacts_target": CONTACTS_PER_ACCOUNT[acct["tier"]],
            }

    sendable = [a for a in accounts if a["outbound_eligible"]]
    for wave in (1, 2, 3):
        subset = [a for a in sendable if a["wave"] == wave]
        with open(out / f"wave{wave}_accounts.csv", "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(_rows(subset))

    with open(out / "all_accounts.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(_rows(accounts))

    with open(out / "suppression_upload.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["account", "route", "note"])
        writer.writeheader()
        for s in suppression:
            writer.writerow({"account": s["account"], "route": s["route"], "note": s["note"]})


# HubSpot portal 242560356 — property internal names from the Import Map tab.
HUBSPOT_FIELDS = [
    "name", "domain", "subindustry", "industry_tier", "revenue_band",
    "ownership_type", "account_segment", "primary_multiplier",
    "icp_fit_score", "account_tier", "outbound_eligible", "warm_only",
    "hq_state", "hq_country",
]


def write_hubspot_export(accounts: list[dict]) -> None:
    out = EXPORTS / "hubspot"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "companies_import.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HUBSPOT_FIELDS)
        writer.writeheader()
        for acct in accounts:
            hq = str(acct["hq"])
            state = hq.split(",")[0].strip() if "," in hq else ""
            country = hq.split(",")[-1].strip() if "," in hq else hq
            writer.writerow({
                "name": acct["company"],
                "domain": acct["primary_domain"],
                "subindustry": acct["vertical"],
                "industry_tier": acct["industry_tier"],
                "revenue_band": acct["revenue_band"],
                "ownership_type": acct["ownership"],
                # HubSpot multi-select import values are semicolon separated.
                "account_segment": ";".join(
                    s.strip() for s in str(acct["segments"]).split(",")
                ),
                "primary_multiplier": acct["primary_multiplier"],
                "icp_fit_score": acct["fit_score"],
                "account_tier": acct["tier"],
                "outbound_eligible": str(acct["outbound_eligible"]).lower(),
                # Cold list: clients and pipeline live on the suppression
                # list, so nothing here is warm-only at import time.
                "warm_only": "false",
                "hq_state": state,
                "hq_country": country,
            })


def write_research_queue(accounts: list[dict]) -> None:
    """Wave 1 research queue: what must be verified before each send."""
    out = EXPORTS / "research"
    out.mkdir(parents=True, exist_ok=True)
    wave1 = [a for a in accounts if a["wave"] == 1]
    lines = [
        "# Wave 1 research queue (days 0-30)",
        "",
        "Tier 1 accounts get 60-90 minutes of research each; Tier 2 gets 20-30.",
        "Nothing sends until the Verification items are confirmed, the conflict",
        "holds are cleared with Sam, and the pre-sequence checklist",
        "(docs/operating-constraints.md) passes. AI maturity /8 and tech",
        "signature /5 are unverified defaults on every row — enrich both and",
        "rescore before finalizing tier (typical lift is +5 to +11 FIT).",
        "",
    ]
    for acct in sorted(wave1, key=lambda a: (-a["fit_score"], a["rank"])):
        flags = []
        if acct["hold"]:
            flags.append("**HOLD — clear with Sam first**")
        if acct["requires_review"]:
            flags.append("review required")
        lines += [
            f"## {acct['rank']}. {acct['company']} — FIT {acct['fit_score']}, {acct['tier']}"
            + (f" ({'; '.join(flags)})" if flags else ""),
            "",
            f"- **Vertical:** {acct['vertical']} | **Segments:** {acct['segments']} | "
            f"**Revenue:** {acct['revenue_band']} | **Ownership:** {acct['ownership']}",
            f"- **Domain:** {acct['primary_domain']} | **In HubSpot:** "
            f"{'yes (' + str(acct['hs_lifecycle']) + ')' if acct['in_hubspot'] else 'no'}",
            f"- **Multiplier [FACT]:** {acct['primary_multiplier']}",
            f"- **Primary use case:** {acct['primary_use_case']} | **Est. first deal:** "
            f"{acct['est_first_deal']} (planning only — client numbers come from the Credit System)",
            f"- **Target titles:** {acct['target_titles']}",
            f"- **Trigger hypotheses [VERIFY]:** {acct['trigger_hypothesis']}",
            f"- **Verify before send:** {acct['verification_required']}",
            f"- **References to cite:** {acct['reference_to_cite']}",
        ]
        if acct["gate_notes"]:
            lines.append(f"- **Gate notes:** {acct['gate_notes']}")
        if acct["notes"]:
            lines.append(f"- **Notes:** {acct['notes']}")
        lines.append("")
    (out / "wave1_research_queue.md").write_text("\n".join(lines), encoding="utf-8")


def write_summary(accounts: list[dict], suppression: list[dict]) -> None:
    out = EXPORTS / "reports"
    out.mkdir(parents=True, exist_ok=True)
    tiers = Counter(a["tier"] for a in accounts)
    waves = Counter(a["wave"] for a in accounts)
    groups = Counter(a["vertical_group"] for a in accounts)
    holds = [a for a in accounts if a["hold"]]
    review = [a for a in accounts if a["requires_review"] and not a["hold"]]
    in_hs = sum(1 for a in accounts if a["in_hubspot"])
    eligible = sum(1 for a in accounts if a["outbound_eligible"])

    lines = [
        "# T100 program summary",
        "",
        f"Accounts: **{len(accounts)}** | Outbound eligible: **{eligible}** | "
        f"Already in HubSpot: **{in_hs}** | Suppressed accounts (clients/pipeline): "
        f"**{len(suppression)}**",
        "",
        "## By tier",
        "",
        "| Tier | Accounts | Contacts target |",
        "|---|---|---|",
    ]
    for tier in ("Tier 1 Named", "Tier 2 Priority", "Tier 3 Volume", "Nurture"):
        n = tiers.get(tier, 0)
        lines.append(f"| {tier} | {n} | {n * CONTACTS_PER_ACCOUNT[tier]} |")
    lines += [
        "",
        "## By wave",
        "",
        "| Wave | Window | Accounts |",
        "|---|---|---|",
        f"| 1 | Days 0-30 | {waves.get(1, 0)} |",
        f"| 2 | Days 31-60 | {waves.get(2, 0)} |",
        f"| 3 | Days 61-90 | {waves.get(3, 0)} |",
        "",
        "## By vertical group",
        "",
        "| Vertical group | Accounts |",
        "|---|---|",
    ]
    for group, n in groups.most_common():
        lines.append(f"| {group} | {n} |")
    lines += [
        "",
        "## Conflict holds — clear with Sam before any outreach",
        "",
    ]
    for acct in holds:
        lines.append(f"- **{acct['company']}** — {acct['notes']}")
    if review:
        lines += ["", "## Flagged for review", ""]
        for acct in review:
            lines.append(f"- **{acct['company']}** — {acct['gate_notes']}")
    lines += [
        "",
        "## Standing caveats",
        "",
        "- AI maturity (/8) and tech signature (/5) are unverified defaults on "
        "every row. FIT scores are floors; enrichment typically adds 5-11 points.",
        "- Reply tracking is SMTP-only and broken. Do not scale send volume "
        "until OAuth reply tracking is verified on a live test.",
        "- All cold sends on Apollo cousin domains, never silverside.ai.",
        "- Human-in-the-loop approval before any send, writeback, or import.",
        "- Deal size columns are planning estimates. Client-facing numbers come "
        "from the Silverside Credit System only.",
        "",
    ]
    (out / "t100_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    accounts, suppression = build_master()
    write_master(accounts, suppression)
    write_apollo_exports(accounts, suppression)
    write_hubspot_export(accounts)
    write_research_queue(accounts)
    write_summary(accounts, suppression)
    eligible = sum(1 for a in accounts if a["outbound_eligible"])
    print(f"Built {len(accounts)} accounts ({eligible} outbound eligible), "
          f"{len(suppression)} suppressed accounts.")
    print(f"Master: {DATA / 't100_master.csv'}")
    print(f"Exports: {EXPORTS}")


if __name__ == "__main__":
    main()
