from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AppConfig:
    apollo_api_key: str
    anthropic_api_key: str
    hubspot_access_token: str
    hubspot_pipeline_id: str
    silverside_facts_path: str
    claude_model: str
    apollo_default_sequence_id: str | None
    apollo_email_account_id: str | None


def load_config() -> AppConfig:
    load_dotenv()
    return AppConfig(
        apollo_api_key=_require("APOLLO_API_KEY"),
        anthropic_api_key=_require("ANTHROPIC_API_KEY"),
        hubspot_access_token=_require("HUBSPOT_ACCESS_TOKEN"),
        hubspot_pipeline_id=os.getenv("HUBSPOT_PIPELINE_ID", ""),
        silverside_facts_path=os.getenv("SILVERSIDE_FACTS_PATH", "silverside_facts.yaml"),
        claude_model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        apollo_default_sequence_id=os.getenv("APOLLO_DEFAULT_SEQUENCE_ID"),
        apollo_email_account_id=os.getenv("APOLLO_EMAIL_ACCOUNT_ID"),
    )


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Required env var {key!r} is not set. Copy .env.example to .env and fill it in.")
    return val
