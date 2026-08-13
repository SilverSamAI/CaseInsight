# Sequence: AI transformation (cross-vertical)

| Field | Value |
|---|---|
| Apollo filter set | Set F — AI transformation, cross vertical (**highest expected reply rate in the model — overweight this**) |
| Target list | All Tier 1 and Tier 2 verticals; titles containing Generative AI / Head of AI / Innovation / Emerging Technology within Marketing, Brand, Creative, or Digital |
| Personas | Head of Generative AI, Head of Innovation, Chief AI Officer (marketing-adjacent) |
| Cadence | 4 emails over 16 days, cousin domain only |
| References cleared | Coca-Cola, Amazon, Panasonic |
| Angle | Pilot-to-production. Governance, not capability. Technical depth, never a deck |
| Standing note | This persona rarely holds budget. Identify the economic buyer on call one and pair with a marketing budget owner |

Merge fields: `{{first_name}}`, `{{company}}`, `{{initiative_reference}}` (their actual pilot, hire, or public statement — required), `{{personalization_line}}`.

---

## Email 1 — Day 1

**Subject:** governance, not capability

Hi {{first_name}},

Most AI content pilots I see don't fail on capability. They fail on brand governance and on nobody owning the review layer, so the output never gets approved for public-facing use.

{{initiative_reference}}

We build the production side of that equation: governed pipelines with human-in-the-loop review, audit trails, and rights management — the layer between a promising pilot and 7 billion impressions of shipped, public-facing work. Coca-Cola, Amazon, and Panasonic are references.

Want to compare notes on what's holding up in production versus what's still demo grade?

---

## Email 2 — Day 4

**Subject:** where AI content actually breaks

{{first_name}} — the honest version of the vendor landscape: plenty of teams have shipped impressive demos. The question worth putting to all of us is who has shipped governed, public-facing work at volume.

The failure points are consistent — product fidelity, claim compliance, review ownership, and asset rights — and none of them are model problems. They're systems problems. Happy to send our governance framework so you can compare it against whatever else you're evaluating.

Worth a quick chat next week?

---

## Email 3 — Day 9

**Subject:** pilot to production

Hi {{first_name}},

A pattern from the deployments that made it out of pilot: the workstream was real (not a demo brief), the brand system was trained before generation started, and review was owned by a named person with authority to reject.

If {{company}} has a pilot that proved capability but stalled at approval, that's the exact profile we work with — the fix is usually the governance architecture, not the model. AdAge named us Standout Agency of the Year 2026 for precisely this kind of work.

Open to a working session with our engineering lead rather than a sales call?

---

## Email 4 — Day 16

**Subject:** closing the loop

{{first_name}} — last note from me.

Whoever gets your AI content program from pilot to production, the hard part will be governance, review, and rights — not generation. If it's useful to sanity-check an architecture against one that's shipping at volume, the offer stands.

---

## Pre-send gate (all items required — see docs/operating-constraints.md)

- [ ] Account passes the pre-sequence checklist; FIT ≥ 45; not suppressed; conflict holds cleared
- [ ] Every address verified; no catch-all; no guessed patterns
- [ ] `{{initiative_reference}}` cites a real, verified initiative — this buyer punishes vagueness fastest
- [ ] Claim gate passed: `python -m caseinsight.claims sequences/ai-transformation.md`
- [ ] Sam has reviewed and approved the send
