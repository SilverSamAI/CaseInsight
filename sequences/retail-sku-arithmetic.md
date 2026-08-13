# Sequence: Retail SKU arithmetic

| Field | Value |
|---|---|
| Apollo filter set | Set B — Omnichannel retail and mass merchant |
| Target list | T100 \| Vertical \| Omnichannel Retail |
| Personas | VP E-commerce, VP Retail Media, Head of Creative Operations, VP Digital Content |
| Cadence | 4 emails over 16 days, cousin domain only |
| References cleared | Sam's Club, Amazon, Williams Sonoma |
| Angle | SKU times channel arithmetic. Photography does not reach the end of the catalogue |

Merge fields: `{{first_name}}`, `{{company}}`, `{{sku_estimate}}`, `{{personalization_line}}`.

---

## Email 1 — Day 1

**Subject:** SKU coverage across channels

Hi {{first_name}},

Quick question: what share of {{company}}'s catalogue has a full content set versus a single image?

You have somewhere north of {{sku_estimate}} SKUs and at least five channels that each want different assets. Photography does not reach the end of that catalogue. A trained product model does.

{{personalization_line}}

We run this for Sam's Club and Williams Sonoma — 20x content volume, at retailer spec, with product fidelity held to reference photography.

Curious what your number is. 15 minutes?

---

## Email 2 — Day 4

**Subject:** product fidelity is the real gate

{{first_name}} — the objection we hear from every retail content team is the right one: product fidelity has to be exact.

Agreed. That's the technical gate, and it's testable. We train on your product photography — typically six to twelve reference images per SKU — and the fidelity question gets settled by looking at output next to the physical product, not by a demo reel.

Happy to run that on one SKU and let the output make the argument.

Worth a quick chat next week?

---

## Email 3 — Day 9

**Subject:** vendor-funded creative demand

Hi {{first_name}},

If {{company}} operates retail media, you're sitting on creative demand with its own P&L: advertisers capped by creative supply, not media appetite.

Amazon is a reference here. Advertiser-facing creative at network scale is a margin product most retail media teams aren't selling yet, because production couldn't keep pace. That constraint is now removable — and the weekly promo calendar and PDP backlog come along with it.

Open to taking a look?

---

## Email 4 — Day 16

**Subject:** closing the loop

{{first_name}} — last note from me.

The catalogue coverage gap doesn't close with more photography budget; the arithmetic doesn't work at your SKU count. If content coverage, promo velocity, or retail media creative becomes a priority this year, happy to show the system and the unit economics whenever it's useful.

---

## Pre-send gate (all items required — see docs/operating-constraints.md)

- [ ] Account passes the pre-sequence checklist; FIT ≥ 45; not suppressed; conflict holds cleared
- [ ] Every address verified; no catch-all; no guessed patterns
- [ ] `{{personalization_line}}` and `{{sku_estimate}}` populated from verified research
- [ ] Claim gate passed: `python -m caseinsight.claims sequences/retail-sku-arithmetic.md`
- [ ] Sam has reviewed and approved the send
