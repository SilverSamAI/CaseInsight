from __future__ import annotations
import json
import re
import time
from typing import Callable
from ..models import Prospect, EmailDraft
from ..config import AppConfig
from .prompt_builder import build_system_prompt, build_user_prompt
from .validator import validate_draft
from ..personas import infer_persona


def generate_email(
    prospect: Prospect,
    facts: dict,
    config: AppConfig,
    context_notes: str = "",
) -> EmailDraft:
    import anthropic

    client = anthropic.Anthropic(api_key=config.anthropic_api_key)
    persona = infer_persona(prospect.title)
    system_prompt = build_system_prompt(facts, persona=persona)
    user_prompt = build_user_prompt(prospect, context_notes)

    response = client.messages.create(
        model=config.claude_model,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    subject, body = _parse_response(response.content[0].text)
    draft = EmailDraft(subject=subject, body=body, prospect=prospect)
    return validate_draft(draft, facts)


def generate_batch(
    prospects: list[Prospect],
    facts: dict,
    config: AppConfig,
    context_notes: str = "",
    on_progress: Callable[[int, int], None] | None = None,
) -> list[EmailDraft]:
    drafts = []
    for i, prospect in enumerate(prospects):
        draft = generate_email(prospect, facts, config, context_notes)
        drafts.append(draft)
        if on_progress:
            on_progress(i + 1, len(prospects))
        if i < len(prospects) - 1:
            time.sleep(1.0)
    return drafts


def _parse_response(text: str) -> tuple[str, str]:
    try:
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
        data = json.loads(cleaned)
        return str(data.get("subject", "")), str(data.get("body", ""))
    except (json.JSONDecodeError, AttributeError):
        pass
    subject_match = re.search(r'"subject"\s*:\s*"([^"]+)"', text)
    body_match = re.search(r'"body"\s*:\s*"(.*?)"(?:\s*[,}])', text, re.DOTALL)
    subject = subject_match.group(1) if subject_match else "Silverside AI"
    body = body_match.group(1).replace("\\n", "\n") if body_match else text
    return subject, body
