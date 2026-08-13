# CaseInsight — Silverside T100 Cold Outbound Program

Operational build of the **Silverside AI ICP and Prospecting Playbook**
(v1.0, August 2026) and the **Top 100 Cold Outbound Targets** list: the
scored account universe, the eligibility and claim gates the playbook
mandates, launch-ready sequence copy, and import-ready artifacts for
Apollo and HubSpot.

Nothing in this repo sends email or writes to live systems. Every artifact
stages work for human review — **human-in-the-loop approval before any
send, import, or CRM writeback is a standing instruction.**

## Layout

```
docs/
  ICP_and_Prospecting_Playbook.md   The canonical playbook (Sections 1-24 + appendix)
  operating-constraints.md          The 8 non-negotiables + pre-sequence checklist
  90-day-launch-plan.md             Week-by-week launch plan and wave map
  apollo-filter-sets.md             Copy-ready Apollo/Crunchbase filter sets A-H
  hubspot-property-map.md           Portal 242560356 property schema (P0/P1/P2)
data/
  source/                           Original workbook + scored CSV (inputs)
  t100_master.csv                   Canonical merged dataset (100 accounts)
  suppression_list.csv              Do-not-cold-email accounts (clients/pipeline)
caseinsight/
  rubric.py                         100-pt FIT rubric (Section 16.1) + tiers + rescore
  gates.py                          Outbound eligibility gates (Sections 14/16.5/18)
  claims.py                         Claim gate: approved metrics/references, banned phrases
  build.py                          Rebuilds data/ and exports/ from data/source/
sequences/                          The 5 launch sequences (week 5-8), claim-gate clean
exports/
  apollo/                           Wave 1-3 account uploads + suppression upload
  hubspot/                          Company import mapped to portal properties
  research/wave1_research_queue.md  Per-account verification checklist, days 0-30
  reports/t100_summary.md           Program summary: tiers, waves, holds, caveats
tests/                              32 tests: rubric integrity, gates, claim gate
```

## Usage

```bash
pip install openpyxl pytest

python -m caseinsight.build    # regenerate data/ and exports/ from source
python -m caseinsight.claims   # claim-gate every sequence (CI for copy edits)
python -m pytest tests/ -q     # full integrity suite
```

Rescoring after enrichment (AI maturity and tech signature are unverified
defaults on every row — FIT scores are floors):

```python
from caseinsight.rubric import rescore
rescore(components, ai_stage=4, tech_systems_detected=2)
```

## The program in one screen

- **100 accounts**, all Tier 1/Tier 2 verticals, $250M-$10B, each with a
  verified content multiplier. Zero financial services (the Financial
  Services Rule). 99 outbound eligible; 5 on conflict HOLD pending
  clearance from Sam; 2 flagged for CASL review.
- **Tiers:** 27 Tier 1 Named / 49 Tier 2 Priority / 23 Tier 3 Volume /
  1 Nurture. Waves: 53 / 26 / 21 across days 0-90.
- **Five sequences** ready for staging: CPG long tail, retail SKU
  arithmetic, beauty+fashion variant arithmetic, QSR franchise backlog,
  AI transformation (highest expected reply rate — overweight it).
- **Hard gates before anything sends:** OAuth reply tracking live, cousin
  domain migration, Tier 4 purge, suppression list loaded, Pereira
  O'Dell + Serviceplan client lists added, claim gate green, Sam's
  approval on every send.

## Provenance

Built from `data/source/` (the Top 100 workbook, the enriched T100 master,
and the scored targets CSV). The Sales Playbook PDF is a formatted
duplicate of `docs/ICP_and_Prospecting_Playbook.md` and is not committed.
Deal-size columns are planning estimates only — client-facing numbers come
from the Silverside Credit System.
