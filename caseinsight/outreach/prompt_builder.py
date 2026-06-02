from __future__ import annotations
from ..models import Prospect
from ..facts.guardrail import build_approved_facts_block, build_offerings_block

SYSTEM_PROMPT_TEMPLATE = """\
You are a sales copywriter for Silverside AI.

## Your Identity
{positioning_line}

## Approved Facts (use ONLY these - never invent claims)
{approved_facts_block}

## What Silverside AI Offers
{offerings_block}

## Positioning Rules
Position Silverside as: {position_as}
Never position Silverside as: {do_not_position_as}

## Hard Rules
- Do not use em dashes.
- Do not use markdown in the body.
- Do not invent facts, numbers, clients, or claims not listed in Approved Facts above.
- Do not fabricate prospect's private priorities or motivations.

## Output Format
Return a JSON object with exactly two keys: "subject" and "body".
The body must be plain text, 3-5 short paragraphs, under 200 words.
"""


def build_system_prompt(facts: dict) -> str:
    company = facts.get("company", {})
    return SYSTEM_PROMPT_TEMPLATE.format(
        positioning_line=company.get("positioning_line", {}).get("text", ""),
        approved_facts_block=build_approved_facts_block(facts),
        offerings_block=build_offerings_block(facts),
        position_as=", ".join(facts.get("position_as", [])),
        do_not_position_as=", ".join(facts.get("do_not_position_as", [])),
    )


def build_user_prompt(prospect: Prospect, context_notes: str = "") -> str:
    emp_str = f"~{prospect.employee_count:,}" if prospect.employee_count else "unknown size"
    tech_str = ", ".join(prospect.technologies[:5]) if prospect.technologies else "not available"
    parts = [
        f"Write a cold outreach email to {prospect.full_name},"
        f" {prospect.title or 'a leader'} at {prospect.company or 'their company'}"
        f" ({prospect.industry or 'unknown industry'}, {emp_str} employees).",
        f"Technologies they use: {tech_str}.",
    ]
    if context_notes:
        parts.append(context_notes)
    parts.append("The email should feel personal and direct, not templated. Keep it under 200 words.")
    return " ".join(parts)
