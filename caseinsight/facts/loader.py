from __future__ import annotations
import yaml
from pathlib import Path

REQUIRED_KEYS = {
    "company", "clients", "metrics", "proof_points",
    "offerings", "position_as", "do_not_position_as", "forbidden_in_copy",
}


def load_facts(path: str) -> dict:
    data = yaml.safe_load(Path(path).read_text())
    if not data:
        raise ValueError(f"{path} is empty")
    missing = REQUIRED_KEYS - set(data.keys())
    if missing:
        raise ValueError(f"silverside_facts.yaml missing required keys: {missing}")
    return data


def get_approved_clients(facts: dict) -> list[str]:
    return [c["name"] for c in facts.get("clients", []) if c.get("outbound_use") == "approved"]


def get_unapproved_clients(facts: dict) -> list[str]:
    return [c["name"] for c in facts.get("clients", []) if c.get("outbound_use") != "approved"]


def get_approved_metrics(facts: dict) -> list[dict]:
    return [m for m in facts.get("metrics", []) if m.get("usage") == "approved_for_outbound"]


def get_approved_proof_points(facts: dict) -> list[dict]:
    return [p for p in facts.get("proof_points", []) if p.get("usage") == "approved_for_outbound"]


def get_forbidden_terms(facts: dict) -> list[str]:
    return facts.get("forbidden_in_copy", [])
