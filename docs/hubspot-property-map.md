# HubSpot property map — portal 242560356

Create these properties **before** importing `exports/hubspot/companies_import.csv`.
Owner ID 79447606. Human-in-the-loop approval required before any writeback to
live records. **P0 properties gate outbound and must exist before the first send.**

## Company properties

| Workbook column | HubSpot property | Type | Allowed values / formula | Required | Priority |
|---|---|---|---|---|---|
| Company | `name` | Text | — | Yes | **P0** |
| Vertical | `subindustry` | Dropdown | 38 values from Playbook Section 3.1 | Yes | **P0** |
| (derived) | `industry_tier` | Dropdown | Tier 1 / Tier 2 / Tier 3 / Tier 4 | Yes | **P0** |
| Est. Revenue Band | `revenue_band` | Dropdown | 9 bands from Playbook Section 2.A | Yes | **P0** |
| (from Apollo) | `annualrevenue` | Number, currency | Actual or estimate | Yes | **P0** |
| HQ | `hq_state` / `hq_country` | Text | Standard | Yes | P1 |
| Ownership | `ownership_type` | Dropdown | Public / Private / PE backed / VC backed / Family owned / Subsidiary / Franchise / Holding co | Yes | **P0** |
| Segment | `account_segment` | **Multi-select** | S1 through S14 | Yes | P1 |
| Primary Multiplier | `primary_multiplier` | Text, multi-line | Free text with source noted | No | P2 |
| Brands count | `brand_count` | Number | Integer | CPG / multi-brand | P1 |
| SKU count | `sku_count_estimate` | Number | Integer | Retail, CPG, fashion, beauty | P1 |
| Markets count | `market_count` | Number | Integer | No | P1 |
| Locations count | `location_count` | Number | Integer | Franchise and multi-unit | P1 |
| (derived) | `expansion_vector_count` | Number | brands + markets + channels + categories | No | P2 |
| Media /6 input | `active_meta_creatives` | Number | Integer. Source: Meta Ad Library | No | P1 |
| Spend /8 input | `marketing_spend_estimate` | Number, currency | EDGAR advertising expense or estimate | No | P1 |
| AI /8 input | `ai_maturity_stage` | Dropdown | 1–8, Playbook Section 12 | No | P1 |
| Tech /5 input | `technology_stack` | Multi-select | DAM / PIM / CMS / commerce / CDP / creative automation / gen AI tools | No | P2 |
| (derived) | `tech_signature_score` | Number | 0–5, calculated | No | P2 |
| Trigger Hypothesis | `active_triggers` | **Multi-select** | Trigger taxonomy from Playbook Section 9 | No | P1 |
| (on detection) | `trigger_last_detected` | Date | — | No | P1 |
| FIT SCORE | `icp_fit_score` | Number | 0–100 | Yes | **P0** |
| TIER | `account_tier` | Dropdown | Tier 1 Named / Tier 2 Priority / Tier 3 Volume / Nurture / Disqualified | Yes | **P0** |
| (external calc) | `intent_score` | Number | 0–50, time decayed. Recompute **weekly** in CLAW/SAGE Postgres | Yes | P1 |
| (manual) | `relationship_score` | Number | 0–25 | No | P1 |
| (manual) | `opportunity_score` | Number | 0–25 | No | P2 |
| (external calc) | `total_priority_score` | Number | (FIT×.45)+(INTENT×.25)+(RELATION×.10)+(OPPTY×.20) | Yes | P1 |
| (gate) | `outbound_eligible` | Boolean | True when `icp_fit_score` ≥ 45 and not suppressed. **Gates Apollo enrolment** | Yes | **P0** |
| (gate) | `warm_only` | Boolean | True when `relationship_score` ≥ 15. **Blocks cold sequences** | Yes | **P0** |
| (on DQ) | `disqualification_reason` | Dropdown | Categories from Playbook Section 14. Required when disqualified | Yes when DQ | P1 |

## Deal properties

| Workbook column | HubSpot property | Type | Allowed values | Required | Priority |
|---|---|---|---|---|---|
| Primary Use Case | `primary_use_case` | Dropdown | 28 use cases from Playbook Section 5.1 | Yes | P1 |
| Est. First Deal | `amount` | Number, currency | **From the Silverside Credit System only, never the workbook estimate** | Yes | **P0** |
| (at creation) | `deal_attribution` | Dropdown | Engine (cold outbound via CLAW/SAGE) / Inbound / Partner / Referral / Network / Expansion | Yes | **P0** |

## Contact properties

| Workbook column | HubSpot property | Type | Allowed values | Required | Priority |
|---|---|---|---|---|---|
| Target Titles | `jobtitle` | Text | Verified title | Yes | **P0** |
| (derived) | `title_category` | Dropdown | 11 categories from Playbook Section 22.2 | Yes | **P0** |
| (derived) | `persona` | Dropdown | P1–P7 from Playbook Section 6 | Yes | P1 |
| (calc) | `contact_score` | Number | 0–50, Playbook Section 17.1 | Yes | P1 |
| (derived) | `contact_priority` | Dropdown | Primary / Strong / Supporting / Backup / Do not contact | Yes | P1 |
| (gate) | `outbound_channel` | Dropdown | Apollo cold / HubSpot warm / Do not contact. **Enforces cold–warm separation** | Yes | **P0** |
| (from LinkedIn) | `months_in_role` | Number | Integer. Score 3–9 months highest | No | P1 |

## Scoring constraints

- HubSpot calculated properties cannot express time decay. Compute
  `intent_score` and `total_priority_score` externally (CLAW/SAGE Postgres)
  and write back weekly — with human approval.
- Reply tracking is SMTP-only and broken: intent component 4 (engagement)
  is directional only until OAuth is live.
- `notes_last_contacted` is corrupted by the Apollo evening bulk sync —
  never use it in list logic.
