# The Agent Layer: Architecture

This document specifies the proposed agent layer for the Silverside sales pipeline. Each agent below uses the standard format (purpose, trigger, systems, inputs, steps, approval, output, storage, risk, first version, advanced version).

**Terminology:** "Forge" refers to the existing local-worker pipeline; "new" means built from scratch this round.

## Summary

| # | Agent | Trigger | Writes anything? | Send authority? |
|---|-------|---------|------------------|-----------------|
| 1 | Signal harvester | Daily cron | No (Slack digest only) | No |
| 2 | Dossier & persona enrichment | On demand | Low-risk HubSpot metadata | No |
| 3 | Hyper-personalization drafting | After Agent 2 / batch | Draft fields in HubSpot | No |
| 4 | Claims QA | After Agent 3 / batch | Status field only | No |
| 5 | Human approval router | Cron poll (30–60 min) | No (human flips status) | No |
| 6 | Sequencer / send | Approved status | Apollo enrollment / Gmail draft | Gated by tool surface |
| 7 | Reply triage & meeting booking | Poll every 2 hours | Slack digest + HubSpot note | No |
| 8 | Weekly sales update compiler | Weekly cron (Monday) | No (draft only) | No |

---

## Agent 1: Signal harvester

**Purpose:** Continuously surface accounts showing real buying signal (funding, hiring, headcount growth, leadership change) inside the five locked verticals, before any human spends enrichment time on them.

**Trigger:** Claude Code Remote cron, daily, e.g. `0 13 * * *` (early morning Pacific).

**Systems involved:** Apollo, Clay, web search, HubSpot (dedupe check).

**Inputs:** The five existing Apollo saved searches (CPG/Beverage, Retail/Hospitality, D2C/Growth, Premium/Luxury, hiring-signal).

**Steps:**
1. Run `apollo_mixed_companies_search` against the saved filters.
2. Cross-check `apollo_organizations_job_postings` for hiring-signal accounts.
3. `web_search` for recent funding/leadership news on top candidates.
4. `search_crm_objects` in HubSpot to drop anything already in active pipeline.
5. Rank the rest.

**Human approval required:** None for the scan itself. Nothing gets touched outside read-only search.

**Output:** Ranked digest, 10 to 20 accounts with the specific trigger reason for each.

**Where stored:** Posted to a Slack channel or DM (Sam or Marius), not written to HubSpot yet. Keeps low-confidence signal out of the CRM.

**Risk:** Apollo org search and job-postings calls consume credits; the tool itself requires confirming "this will consume 1 credit" per call, so cost is visible, not hidden.

**Suggested first version:** Daily Slack digest, no writes anywhere.

**Future advanced version:** Auto-score against the three-tier ICP model and auto-create a HubSpot company record (no contact, no sequence) for anything above the threshold, so Agent 2 has something to enrich without a human copy-pasting a domain.

---

## Agent 2: Dossier and persona enrichment agent

**Purpose:** Turn a flagged account into the structured profile that makes Agent 3's draft actually personalized instead of templated.

**Trigger:** Fired on demand (Sam or Marius react to the Signal Harvester digest, or name an account directly).

**Systems involved:** Apollo, Clay, HubSpot, Fireflies, Google Drive.

**Inputs:** Company domain or contact name.

**Steps:**
1. `apollo_mixed_people_api_search` for the three target personas (economic buyer, operational owner, champion).
2. `apollo_organizations_enrich` for firmographics.
3. Clay `add-company-data-points` for tech stack and recent news.
4. `get_crm_objects` / `search_crm_objects` in HubSpot for existing relationship history.
5. `fireflies_search` for any prior call touching this account or contact.
6. Drive `search_files` for past SOWs or case studies in the matching vertical.

**Human approval required:** None for read/enrich. Writing `claw_persona_role` and `claw_silverside_vertical` onto the HubSpot record is low-risk metadata, not a deal-stage change, so this can run without a per-record approval (owner's call).

**Output:** A one-page dossier (persona, vertical, trigger event, relevant proof point, any existing relationship history) plus the populated HubSpot fields using the existing de-dup schema, not new fields.

**Where stored:** HubSpot contact/company properties + a Drive or Notion brief.

**Risk:** Apollo enrichment and Clay data points both cost credits per record; batch confirmation needed if run across a list rather than one account at a time.

**Suggested first version:** One account at a time, on demand.

**Future advanced version:** Batch mode against the full Tier 1 list, with upfront total-credit-cost confirmation per Apollo's own tool requirements.

---

## Agent 3: Hyper-personalization drafting agent

**Purpose:** Produce the actual draft, using the dossier instead of a fixed template, while staying inside the approved claims allowlist.

**Trigger:** Fires when Agent 2 finishes a dossier, or batch-run over a backlog.

**Systems involved:** HubSpot, Google Drive, Forge's existing assembler logic.

**Inputs:** The dossier, the locked vertical/persona framework, the approved metrics (68% cost reduction, 87.5% time reduction, 20x content volume, 7B impressions), the approved reference-client list, the style rules (no em dashes, no "circling back," low-friction CTA).

**Steps:**
1. Pull dossier fields.
2. Pull 1 to 2 winning past examples from Drive as style reference, not copy source.
3. Draft using Claude's reasoning over the dossier rather than pure template-fill, since that's the actual upgrade over what Forge does today.
4. Stage the draft.

**Human approval required:** Never sends. Output is a draft only.

**Output:** Draft body in `claw_email_draft_body`, status set to `pending_qa`.

**Where stored:** HubSpot custom fields, same schema already built.

**Risk:** None until Agent 4 clears it. This is the step most likely to need real engineering time, since "personalize with Claude reasoning" is a meaningfully different code path than "fill a template," and Forge's current assembler structure hasn't been read yet.

**Suggested first version:** Wire this in as an additional drafting mode inside the existing assembler rather than a parallel system, once the actual code has been read.

**Future advanced version:** A/B the reasoning-based draft against the template draft on reply rate, not just ship the new one blind.

---

## Agent 4: Claims QA agent

**Purpose:** This is the one that actually unblocks the backlog. Verify every metric and client reference in a draft against the approved allowlist before a human ever sees it.

**Trigger:** Immediately after Agent 3, or run once now in batch against everything currently sitting at `pending_qa` or stuck.

**Systems involved:** The existing `claim_verifier.py` logic if that's still how Forge does it, or its current equivalent inside the repo.

**Inputs:** Draft body, the facts allowlist, the approved client list.

**Steps:**
1. Run the deterministic verifier (keep it deterministic, don't replace it with an LLM "vibe check" since exact-match matters for compliance).
2. On fail, identify the specific unapproved claim.
3. Ask Claude to rewrite that sentence using only allowlisted facts, or cut it.
4. Re-run.
5. After N failed attempts, escalate to a human with the exact violation cited instead of looping forever.

**Human approval required:** This agent is the gate for content accuracy, not the gate for sending. No send authority.

**Output:** Pass moves status to `pending_human_review`. Fail-after-N escalates with a specific, named reason.

**Where stored:** `claw_email_draft_status` field, same schema.

**Risk:** Low. This is mostly deterministic text matching, not generative risk.

**Suggested first version:** Run this once, now, against the current backlog to find out how many of the 112 actually clear with a clean rewrite versus how many need a human rewrite. That number alone tells you if this is a one-afternoon fix or a real problem with how Forge drafts.

**Future advanced version:** Feed common violation patterns back into Agent 3's prompt so the same unapproved claim stops recurring. That's a real, lightweight version of the "meta_skill" learning loop the watchdog is already checking for, applied to claims compliance specifically.

---

## Agent 5: Human approval router

**Purpose:** Make the approval gate a clean, low-friction action instead of digging through HubSpot.

**Trigger:** Claude Code Remote cron poll, every 30 to 60 minutes, checking for `claw_email_draft_status = pending_human_review`.

**Systems involved:** HubSpot, Slack.

**Inputs:** Drafts at that status.

**Steps:**
1. Pull the draft, prospect name, company, and trigger reason.
2. Post to Slack as a digest with the draft text inline.
3. Wait for status change in HubSpot (Sam or Marius flip it manually; that flip is the actual approval, not anything automated).

**Human approval required:** This entire agent's purpose is the approval step. There's no code-level bypass.

**Output:** Routes anything flipped to `approved` to Agent 6.

**Where stored:** Status field drives the workflow.

**Risk:** This is polling, not a webhook. No HubSpot webhook tool exists in this environment, so there's a 30 to 60 minute lag between approval and send, not instant. Worth knowing going in.

**Suggested first version:** Exactly as above.

**Future advanced version:** A real HubSpot webhook receiver (custom-built, outside MCP, a genuine engineering project if zero lag is wanted).

---

## Agent 6: Sequencer / send agent

**Purpose:** Move an approved draft into the actual channel.

**Trigger:** Approved status detected by Agent 5.

**Systems involved:** Apollo for cold (cousin domains), Gmail for warm.

**Inputs:** Approved draft + channel determination (cold vs warm, per the existing data architecture rule).

**Steps, cold path:**
1. `apollo_contacts_search` or `apollo_contacts_create` if needed.
2. `apollo_emailer_campaigns_search` for the right sequence.
3. `apollo_email_accounts_index` for sender.
4. `apollo_emailer_campaigns_add_contact_ids` to enroll.

**Steps, warm path:**
1. `create_draft` in Gmail.

**Human approval required:** Built into the tools themselves, not just policy. Apollo's enrollment tool requires presenting a confirmation summary (sender, sequence, contact count, active/paused) and waiting for explicit approval before it will run — by its own description, not by anything added on top. Gmail's connector only exposes `create_draft`; there's no send function available here at all, so a human has to physically open Gmail and hit send. Both channels are gated by the tool surface itself.

**Output:** Apollo enrollment or a Gmail draft sitting in the inbox.

**Where stored:** Native to each platform.

**Risk:** Low, given the above. The real risk is upstream (a bad draft reaching this stage), not here.

**Suggested first version:** As described.

**Future advanced version:** None needed. This stage is already as safe as the tools allow.

---

## Agent 7: Reply triage and meeting booking agent

**Purpose:** Catch replies fast and draft the response, without auto-sending anything to a real prospect.

**Trigger:** Poll every 2 hours.

**Systems involved:** Gmail, HubSpot, Google Calendar.

**Inputs:** Recent outbound thread IDs.

**Steps:**
1. `search_threads` / `get_thread` in Gmail for replies.
2. Classify (positive, neutral, negative, OOO, unsubscribe).
3. Cross-check HubSpot status.
4. On positive, `suggest_time` in Calendar and draft a scheduling reply.

**Human approval required:** No auto-send of replies. Calendar invites to external attendees should be confirmed before creation, since an invite is itself outbound communication to a real person.

**Output:** Slack digest of classified replies with a draft response attached for one-click use.

**Where stored:** Slack, plus a HubSpot note.

**Risk:** HubSpot reply tracking is reportedly broken (SMTP-only connection, not full OAuth), so Gmail-side detection is the reliable channel right now, not HubSpot's own activity feed. Worth fixing the OAuth connection independent of this agent, since it undermines CRM-side reply visibility generally.

**Suggested first version:** As described, Gmail-sourced.

**Future advanced version:** Once OAuth is fixed, cross-validate against HubSpot's native reply tracking and use disagreement between the two as a data-quality alarm.

---

## Agent 8: Weekly sales update compiler

**Purpose:** Automate the Monday update currently run by hand.

**Trigger:** Weekly cron, Monday early morning.

**Systems involved:** HubSpot, Apollo.

**Inputs:** MTD send volumes for Sam and Marius.

**Steps:**
1. `apollo_analytics_sync_report` for Apollo-side MTD metrics.
2. HubSpot `query_crm_data` for HubSpot-side volumes, sourced from the correct field, not `notes_last_contacted` (known to be inflated by Apollo's evening bulk sync on 631+ records).
3. Resolve owner IDs via `search_owners` rather than hardcoding, so the Hailey/Natalie owner-ID mismatch doesn't repeat.
4. Compile into the existing format.

**Human approval required:** Draft only; a human sends.

**Output:** Drafted Slack message or Gmail draft, ready to edit.

**Where stored:** N/A, transient.

**Risk:** Entirely about source data quality, not the agent logic. Garbage in, garbage out, on both known bugs above.

**Suggested first version:** As described.

**Future advanced version:** Trend lines over the prior 4 weeks, not just the current MTD snapshot.

---

## Forge core migration (infrastructure, not a new agent)

This is the highest-leverage single change available, separate from anything above. Move `run_forge_orchestrator`, `run_forge_meta_skill`, and `run_forge_prompt_tuning` off the local arq worker and onto Claude Code Remote triggers in the SilverSales environment, the same way `forge-watchdog` and `forge-branch-janitor` already run.

**What this buys:** the entire generation pipeline stops depending on a laptop being on.

**What it costs:** someone has to read how the arq worker currently invokes those three jobs and translate that into trigger prompts pointed at the same repo, which is real but bounded engineering work, not a rebuild.

This should be sequenced before most of the new agents above, since Agents 1 through 4 are only as valuable as the pipeline they feed, and right now that pipeline has a single point of failure that's already been important enough to build a watchdog around.

---

## LinkedIn Sales Navigator: the honest version

No connector exists for it in this environment, and there's no general-purpose, compliant API for Sales Navigator search or export that can be wired up. The two real paths:

1. **Official CRM sync.** If Silverside is on Sales Navigator Advanced or Advanced Plus, LinkedIn offers an official CRM sync to certain platforms including HubSpot, but that's configured on LinkedIn's side by a LinkedIn admin, not something buildable from here. Worth checking with whoever owns the Sales Navigator seat.
2. **Manual layer.** Otherwise, treat LinkedIn as a manual layer: Pete Callahan's 6,000-person network gets checked for mutual connections and warm paths by a human, and that finding gets typed into a HubSpot field the agents above can then read. That's slower, but it's the only path that doesn't carry ToS exposure.

Apollo and Clay already cover most of the structured data Sales Navigator would otherwise provide (titles, seniority, tech stack, headcount growth, funding), so the actual gap is narrower than it might feel.

---

## Build order

1. **Run Agent 4 (claims QA) once, now**, against the current draft backlog. Lowest effort, answers the most important open question: is this a quick fix or a structural problem.
2. **Confirm current Apollo send volume.** If it's still at or near zero, that's the real fire, and Agents 1 to 3 are pointless until outbound is actually flowing again.
3. **Migrate the Forge core loop off the local worker** (section above). Removes the single point of failure everything else depends on.
4. **Stand up Agents 1, 2, 5, 6** (signal, dossier, approval router, sequencer) as the new intelligence layer feeding the now-cloud-hosted Forge.
5. **Agent 8 (weekly compiler)** can be built in parallel any time; it has no dependencies on the above.
6. **Agent 7 (reply triage)** after the HubSpot OAuth fix, or accept Gmail-only detection as a known limitation.

---

## Open questions before building against the real repo

1. Is the 112-stuck-drafts figure from memory still current, or has Forge's `meta_skill`/`prompt_tuning` loop already addressed it?
2. Do `forge: auto-generate` commits represent code, email drafts, or both? Changes exactly where Agents 1 to 4 plug in.
3. Is Apollo cold outbound still flat, or has that been resolved since March?
4. Should `SilverSamAI/Claw-SDR-AI` be added to a session so `apps/worker/settings.py` and the assembler/verifier code can actually be read, so Agents 3 and 4 above get built against what's really there instead of what's inferred from a watchdog's health-check script?
