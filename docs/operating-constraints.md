# Operating constraints — non-negotiable

Standing instructions from Playbook Section 18.1. These govern every send,
import, and writeback in this program.

1. **All cold sending on Apollo cousin domains. Never on silverside.ai primary.**
   The audit found cold sequences on primary producing an 8%+ bounce rate.
   Migration precedes any volume increase.
2. **HubSpot is warm contacts only. Apollo handles cold.** A contact with
   `relationship_score` ≥ 15 never enters a cold sequence.
3. **Human-in-the-loop approval before any send.** No exceptions. The same
   applies to any CRM writeback to live records and any Apollo/HubSpot import.
4. **Approved metrics only:** 68 percent cost reduction, 87.5 percent time
   reduction, 20x content volume, 7 billion impressions. Enforced by
   `python -m caseinsight.claims`.
5. **Approved cold reference clients only:** Coca-Cola, Amazon, Sephora and
   LVMH, Sam's Club, Williams Sonoma, BMW, PacSun, Marc Jacobs, Quay,
   SimpliSafe, CyberArk, Headline, Svedka, Panasonic, Goodwill. The broader
   boilerplate list (Adobe, Fifth Third Bank, ...) is approved for RFPs,
   credentials, and SOW company overviews — **not for cold email**.
6. **Reply tracking is SMTP-only and broken for reply measurement.** Do not
   scale volume until OAuth is implemented; performance that cannot be
   measured cannot be optimized.
7. **`notes_last_contacted` is corrupted** by the Apollo evening bulk sync on
   600+ records. Never use it as a freshness signal in list logic.
8. **No direct cold sequences into Germany or France** (Serviceplan
   partner-led only). **Canada requires CASL review** before any send —
   affects Savers Value Village and Bausch + Lomb specifically.

## Minimum data requirements before an account enters a sequence (18.2)

| Field | Requirement | Reject if missing |
|---|---|---|
| Company name and domain | Verified, canonical | **Yes** |
| Industry and subindustry | Mapped to Section 3 taxonomy | **Yes** |
| Revenue estimate | Within a defined band | **Yes** |
| Employee count | Within a defined band | No, but scores 0 |
| `icp_fit_score` | 45 or above | **Yes** |
| At least one multiplier verified | Brands, SKUs, markets, or locations | **Yes** |
| 2+ contacts with contact score ≥ 24 | Verified titles | **Yes** |
| Email verification | Valid; not catch-all; not guessed | **Yes — this is the bounce-rate fix** |
| Suppression check | Not a client, not warm in HubSpot, not opted out, not a competitor | **Yes** |
| One personalization input | Trigger, multiplier arithmetic, or public statement | **Yes for Tier 1/2. Optional Tier 3** |

## Pre-sequence checklist (24.12) — all items required

```
ACCOUNT
[ ] Industry is Tier 1 or Tier 2 per Section 3
[ ] Revenue is $250M to $10B, or $100M+ with a $20M+ raise inside 18 months
[ ] At least one multiplier verified with a source noted:
      3+ brands / 500+ SKUs / 100+ locations / 5+ markets
[ ] icp_fit_score is 45 or above
[ ] Not in the suppression list: not a current client, not active pipeline,
    not previously opted out, not a competitor
[ ] warm_only is false. If relationship_score is 15+, route to HubSpot warm
[ ] Not headquartered in Germany, France, or Canada
[ ] subindustry, revenue_band, and account_tier are populated in HubSpot

CONTACTS
[ ] 2 or more contacts with contact_score of 24 or above
[ ] At least one contact has plausible budget authority for the deal size
[ ] No Legal, Finance, HR, or InfoSec contacts in the sequence
[ ] Every email address verified. No catch all. No guessed patterns
[ ] outbound_channel is set to Apollo cold on every contact

MESSAGE
[ ] Sending from an Apollo cousin domain, never silverside.ai
[ ] Only approved metrics used (68% / 87.5% / 20x / 7 billion)
[ ] Only approved cold reference clients named
[ ] One genuine personalization input per contact for Tier 1 and Tier 2
[ ] Claim gate passed  (python -m caseinsight.claims)
[ ] No banned phrases
[ ] Low friction CTA
[ ] Sam has reviewed and approved the send
```
