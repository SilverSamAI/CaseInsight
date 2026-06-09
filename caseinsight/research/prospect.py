from __future__ import annotations
import time
from dataclasses import replace
from ..models import Prospect
from .apollo_client import ApolloClient, ApolloAPIError


def _map_person(person: dict) -> Prospect:
    org = person.get("organization") or {}
    name_parts = (person.get("name") or "").split(" ", 1)
    techs = [
        t.get("name", "")
        for t in (org.get("current_technologies") or [])
        if t.get("name")
    ]
    return Prospect(
        first_name=person.get("first_name") or (name_parts[0] if name_parts else ""),
        last_name=person.get("last_name") or (name_parts[1] if len(name_parts) > 1 else ""),
        email=person.get("email"),
        title=person.get("title"),
        company=org.get("name") or person.get("organization_name"),
        linkedin_url=person.get("linkedin_url"),
        apollo_id=person.get("id"),
        industry=org.get("industry"),
        employee_count=org.get("estimated_num_employees"),
        technologies=techs,
    )


def search_prospects(
    client: ApolloClient,
    titles: list[str],
    companies: list[str] | None = None,
    industries: list[str] | None = None,
    limit: int = 25,
) -> list[Prospect]:
    raw = client.search_people(
        titles=titles,
        company_names=companies,
        industries=industries,
        per_page=min(limit, 25),
    )
    return [_map_person(p) for p in raw.get("people", [])[:limit]]


def enrich_prospect(client: ApolloClient, prospect: Prospect) -> Prospect:
    if not prospect.email and not prospect.linkedin_url:
        return prospect
    try:
        time.sleep(1.2)
        raw = client.enrich_person(email=prospect.email, linkedin_url=prospect.linkedin_url)
        person = raw.get("person") or {}
        if not person:
            return prospect
        enriched = _map_person(person)
        return replace(
            prospect,
            email=prospect.email or enriched.email,
            title=prospect.title or enriched.title,
            company=prospect.company or enriched.company,
            industry=prospect.industry or enriched.industry,
            employee_count=prospect.employee_count or enriched.employee_count,
            technologies=prospect.technologies or enriched.technologies,
        )
    except ApolloAPIError:
        return prospect


def filter_prospects(
    prospects: list[Prospect],
    require_email: bool = True,
    exclude_domains: list[str] | None = None,
) -> list[Prospect]:
    exclude_domains = exclude_domains or []
    result = []
    for p in prospects:
        if require_email and not p.email:
            continue
        if p.email and any(p.email.lower().endswith(d.lower()) for d in exclude_domains):
            continue
        result.append(p)
    return result
