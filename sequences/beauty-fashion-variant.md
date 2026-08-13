# Sequence: Beauty and fashion variant arithmetic

| Field | Value |
|---|---|
| Apollo filter sets | Set C — Beauty, cosmetics, personal care · Set D — Fashion, apparel, footwear |
| Target lists | T100 \| Vertical \| Beauty & Personal Care · T100 \| Vertical \| Fashion & Footwear |
| Personas | VP Brand, VP E-commerce, Head of Content, Head of Studio, Head of Creative Operations |
| Cadence | 4 emails over 16 days, cousin domain only |
| References cleared | Sephora and LVMH, Marc Jacobs, Quay, PacSun |
| Angle | Shade / colourway combinatorics. Studio augmentation, never photography replacement |

Merge fields: `{{first_name}}`, `{{company}}`, `{{variant_math}}` (their real arithmetic, e.g. "40 shades times 6 channels times 4 markets is 960 assets"), `{{personalization_line}}`.

---

## Email 1 — Day 1

**Subject:** {{variant_math_short}}

Hi {{first_name}},

{{variant_math}}. Curious what that costs {{company}} today, and how long it takes.

{{personalization_line}}

That multiplication is a production budget problem long before it's a creative problem. We build trained brand systems that generate the variant set — shades, colourways, contexts, markets — from your reference photography, with your studio in control. Sephora and LVMH, Marc Jacobs, and Quay are references; work built this way has delivered 7 billion impressions under brand governance.

Worth a quick chat next week?

---

## Email 2 — Day 4

**Subject:** augmentation, not replacement

{{first_name}} — to be direct about what this is and isn't: your photography is your brand. Nobody serious proposes replacing it.

What a trained system replaces is the long tail of derivative work — the channel crops, the market versions, the colourway extensions of a hero shoot — that eats studio capacity without adding craft. Your team art-directs; the system multiplies; every asset passes human review before it ships.

Open to taking a look at how this works?

---

## Email 3 — Day 9

**Subject:** speed to trend

Hi {{first_name}},

The other half of the variant problem is time. A trend window is days; a reshoot cycle is weeks. For the brands we work with, production time came down 87.5 percent — which is the difference between reacting to a trend and watching it pass.

A beauty or fashion buyer decides on the strength of the output, not the deck — so the right next step is a sample run on one launch or one drop, next to your existing photography.

Curious whether that's worth 15 minutes.

---

## Email 4 — Day 16

**Subject:** closing the loop

{{first_name}} — last note from me.

The variant math doesn't get smaller: more channels, more markets, more drops. If the production line behind it becomes the constraint this year, happy to show what the system produces on your products whenever it's useful.

---

## Pre-send gate (all items required — see docs/operating-constraints.md)

- [ ] Account passes the pre-sequence checklist; FIT ≥ 45; not suppressed; conflict holds cleared
- [ ] Every address verified; no catch-all; no guessed patterns
- [ ] `{{variant_math}}` built from verified SKU/shade/colourway counts, not guessed
- [ ] Claim gate passed: `python -m caseinsight.claims sequences/beauty-fashion-variant.md`
- [ ] Sam has reviewed and approved the send
