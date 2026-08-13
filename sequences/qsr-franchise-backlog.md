# Sequence: QSR franchise backlog

| Field | Value |
|---|---|
| Apollo filter set | Set E — QSR, fast casual, restaurants, franchise |
| Target list | T100 \| Vertical \| QSR, Franchise & Hospitality |
| Personas | VP Field / Franchise Marketing, VP Brand Marketing, CMO, Head of Creative |
| Cadence | 4 emails over 16 days, cousin domain only |
| References cleared | Anonymized franchise market evidence only (no named QSR references are cleared for cold) |
| Angle | The local request backlog. Corporate stops being the bottleneck and stops saying no |

Merge fields: `{{first_name}}`, `{{company}}`, `{{location_count}}`, `{{personalization_line}}`.

**Conflict note:** GoTo Foods is on HOLD (Jamba competes with an active pursuit). Clear all holds with Sam before enrolment.

---

## Email 1 — Day 1

**Subject:** what franchisees make when you say no

Hi {{first_name}},

Every local request corporate declines becomes an off-brand asset a franchisee makes anyway. The question is not whether local assets get made — it's whether you control them.

{{personalization_line}}

With {{location_count}} locations, the demand side of that equation never shrinks. We build franchisee self-serve systems with corporate brand control: local market versions on demand, brand standards enforced automatically, human review in the loop.

How many local requests are you turning down each month? Worth a quick conversation.

---

## Email 2 — Day 4

**Subject:** the market math on local production

{{first_name}} — some market evidence from franchise systems we've looked at: a seven-figure campaign shipping with three creative versions, and an $8,000 charge for a type change on a local adaptation.

Nobody defends that math; it's just what agency economics do to small-batch local work. A trained brand system makes the marginal local version close to free, which is what turns the LTO calendar and DMA-level media from a capacity problem into a template problem.

Open to taking a look at how this works?

---

## Email 3 — Day 9

**Subject:** "we tried a portal"

Hi {{first_name}},

The most common response we hear: "we tried a portal and adoption was terrible."

Usually that's an adoption design problem rather than a technology problem. The systems that work ask a franchisee for three inputs and return finished, brand-compliant assets. The ones that fail ask franchisees to be designers. For the brands we work with, production time came down 87.5 percent — and the ad fund pays for assets that actually run.

Worth a quick chat next week?

---

## Email 4 — Day 16

**Subject:** closing the loop

{{first_name}} — last note from me.

The local request backlog is structural: franchisee demand for local assets is effectively unlimited, and corporate can't staff to it. If removing yourself as the bottleneck becomes a priority this year, happy to show the system whenever it's useful.

---

## Pre-send gate (all items required — see docs/operating-constraints.md)

- [ ] Account passes the pre-sequence checklist; FIT ≥ 45; not suppressed; **conflict holds cleared with Sam**
- [ ] Every address verified; no catch-all; no guessed patterns
- [ ] `{{location_count}}` verified against store locator or FDD
- [ ] Claim gate passed: `python -m caseinsight.claims sequences/qsr-franchise-backlog.md`
- [ ] Sam has reviewed and approved the send
