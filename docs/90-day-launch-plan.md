# 90-day outbound launch plan

Wave assignments in `data/t100_master.csv` map to this plan. **Do not
increase send volume until OAuth reply tracking is verified working.**

| Week | Action | Owner | Success measure | Blocks what |
|---|---|---|---|---|
| 1–2 | **Fix infrastructure.** OAuth email connection replacing SMTP. Migrate all cold sequences to Apollo cousin domains. Remediate the 112 staged CLAW drafts to the four approved metrics. Suppress `notes_last_contacted` from all list logic | Sam + RevOps | Bounce rate under 2%. Reply tracking verified functional on a live test | **Everything.** Do not send volume before this |
| 1–2 | Build the HubSpot property schema (all P0 rows in `docs/hubspot-property-map.md`). Backfill `industry_tier`, `subindustry`, `revenue_band` across the existing database | RevOps | Schema live. Existing records classified | Scoring, gating, reporting |
| 2–3 | **Purge Tier 4** from all active sequences. Reclassify the Financial Services 36% against the Financial Services Rule. Load `data/suppression_list.csv` into Apollo | Sam + Marius | Tier 4 at 0% of active cold volume. Suppression list live | List integrity |
| 2–3 | Pull the Pereira O'Dell and Serviceplan active client lists from Rob. Add to suppression | Sam | Channel conflict risk closed | First send |
| 3–4 | Score the existing HubSpot database on FIT. Drop everything under 45 to nurture. Do not enrich anything under 45 | RevOps | Clean tiered universe with a documented drop count | Enrichment spend efficiency |
| 3–5 | Load Wave 1 accounts (`exports/apollo/wave1_accounts.csv`) into Apollo. Enrich AI maturity and tech signature. Rescore (`caseinsight.rubric.rescore`). Pull contacts per the tier mix. Verify every email | Marius + Sam | 400–600 verified contacts staged, all FIT rescored post-enrichment | Sequence launch |
| 4–6 | Work the 1,000-contact prioritized repliers-and-clickers list in parallel with net new | Sam + Marius | 30+ conversations opened from existing intent | Nothing — run concurrently |
| 5–8 | **Launch the five sequences** in `sequences/`: CPG long tail, retail SKU arithmetic, beauty+fashion variant, QSR franchise backlog, AI transformation | Sam | 5 sequences live, 40+ contacts each, human approved | Measurement baseline |
| 6–8 | Launch Filter Set F (AI transformation) across all Tier 1 and Tier 2 verticals — highest expected reply rate in the model | Marius | 60+ contacts. Reply rate benchmarked against the vertical sequences | Model validation |
| 8–10 | Stand up trigger monitoring: executive change alerts, job posting monitors, funding alerts, agency review alerts | RevOps | Triggers detected within 7 days of occurrence | INTENT scoring accuracy |
| 8–12 | Launch the PE sponsor motion: 5 consumer-focused sponsors at operating partner level | Sam | 3+ sponsor conversations opened | Portfolio leverage |
| 10–12 | **First ICP performance review.** Reply, meeting, and close rate by tier, segment, vertical, persona, and trigger. Reweight the scoring model against actual data | Sam + RevOps | Model v2 with empirically reweighted categories. Answer the 10 open questions in the Playbook appendix | Everything after day 90 |
| Ongoing | Human-in-the-loop approval on every send. Cousin domains only. Approved metrics only. Approved cold references only | Sam | 100% compliance | Legal and reputational exposure |

## Wave map

| Wave | Window | Accounts | File |
|---|---|---|---|
| 1 | Days 0–30 | 53 | `exports/apollo/wave1_accounts.csv` + `exports/research/wave1_research_queue.md` |
| 2 | Days 31–60 | 26 | `exports/apollo/wave2_accounts.csv` |
| 3 | Days 61–90 | 21 | `exports/apollo/wave3_accounts.csv` |
