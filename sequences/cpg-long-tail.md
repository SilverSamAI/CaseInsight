# Sequence: CPG long tail

| Field | Value |
|---|---|
| Apollo filter set | Set A — CPG multi brand |
| Target list | T100 \| Vertical \| CPG Multi-Brand |
| Personas | VP Brand Marketing, Head of Creative Operations, VP Shopper Marketing, VP Integrated Marketing |
| Cadence | 4 emails over 16 days, cousin domain only |
| References cleared | Coca-Cola, Svedka |
| Angle | The long tail. Top brands have an agency; the rest of the portfolio has nothing |

Merge fields: `{{first_name}}`, `{{company}}`, `{{personalization_line}}` (required for Tier 1 and 2 sends — trigger, multiplier arithmetic, or a public statement).

---

## Email 1 — Day 1

**Subject:** your other 22 brands

Hi {{first_name}},

Your top three brands have an agency. I'm more curious what happens to the rest of the portfolio, because that's usually where the content gap is widest and the budget is thinnest.

{{personalization_line}}

We build governed AI content systems for multi-brand portfolios — Coca-Cola and Svedka among them — that give the long tail modern content at a cost per asset the tail can actually justify. For the brands we work with, production cost came down 68 percent with output up.

Worth a quick chat next week?

---

## Email 2 — Day 4

**Subject:** the brands the AOR never gets to

{{first_name}} — most portfolio marketing teams we talk to have the same split: the flagship brands get full agency attention, and the other fifteen to forty brands get a resize queue.

The economics of that are structural. An agency retainer can't stretch across the tail, and the tail's revenue can't fund one. A trained brand system can: the retailer-specific versions, seasonal refreshes, and shopper assets the tail needs become marginal-cost work instead of scoped projects.

Open to taking a look at how this works?

---

## Email 3 — Day 9

**Subject:** retailer versions, without the resize queue

Hi {{first_name}},

One number worth knowing: what it costs {{company}} today to produce the Walmart, Target, Kroger, and Amazon versions of a single campaign — across every brand that needs them.

That multiplication is exactly what breaks traditional production economics, and it's what a governed content system absorbs. Brand governance holds because the system is trained on your guidelines, with human review before anything ships — 7 billion impressions have run through work built this way.

Curious what your number is. 15 minutes?

---

## Email 4 — Day 16

**Subject:** closing the loop

{{first_name}} — last note from me.

If the portfolio's long tail is fully served today, ignore this. If it isn't, the gap won't close by adding headcount or stretching the AOR — it closes by changing the cost structure of production itself.

If that becomes a priority this year, happy to show the system and the math whenever it's useful.

---

## Pre-send gate (all items required — see docs/operating-constraints.md)

- [ ] Account passes the pre-sequence checklist; FIT ≥ 45; not suppressed; conflict holds cleared
- [ ] Every address verified; no catch-all; no guessed patterns
- [ ] `{{personalization_line}}` populated with a genuine input for Tier 1/2
- [ ] Claim gate passed: `python -m caseinsight.claims sequences/cpg-long-tail.md`
- [ ] Sam has reviewed and approved the send
