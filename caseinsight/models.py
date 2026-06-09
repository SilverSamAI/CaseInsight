from __future__ import annotations
from dataclasses import dataclass, field, asdict


@dataclass
class Prospect:
    first_name: str
    last_name: str
    email: str | None = None
    title: str | None = None
    company: str | None = None
    linkedin_url: str | None = None
    apollo_id: str | None = None
    industry: str | None = None
    employee_count: int | None = None
    technologies: list[str] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Prospect:
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in valid})


@dataclass
class EmailDraft:
    subject: str
    body: str
    prospect: Prospect
    facts_used: list[str] = field(default_factory=list)
    passed_guardrail: bool = False
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> EmailDraft:
        prospect = Prospect.from_dict(d["prospect"])
        valid = {f.name for f in cls.__dataclass_fields__.values()} - {"prospect"}
        kwargs = {k: v for k, v in d.items() if k in valid}
        return cls(prospect=prospect, **kwargs)


@dataclass
class SyncResult:
    prospect_email: str
    hubspot_contact_id: str | None = None
    hubspot_deal_id: str | None = None
    apollo_contact_id: str | None = None
    apollo_sequence_enrolled: bool = False
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
