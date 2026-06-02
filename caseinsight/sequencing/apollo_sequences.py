from __future__ import annotations
import time
from rich.console import Console
from rich.progress import track
from ..models import Prospect
from ..research.apollo_client import ApolloClient, ApolloAPIError


def upsert_contact_in_apollo(client: ApolloClient, prospect: Prospect) -> str | None:
    if prospect.email:
        try:
            result = client.search_contacts_by_email(prospect.email)
            contacts = result.get("contacts", [])
            if contacts:
                return contacts[0]["id"]
        except ApolloAPIError:
            pass

    try:
        payload = {
            k: v for k, v in {
                "first_name": prospect.first_name,
                "last_name": prospect.last_name,
                "email": prospect.email,
                "title": prospect.title,
                "organization_name": prospect.company,
            }.items() if v is not None
        }
        result = client.create_contact(payload)
        return (result.get("contact") or {}).get("id")
    except ApolloAPIError:
        return None


def enroll_contact(
    client: ApolloClient,
    prospect: Prospect,
    sequence_id: str,
    email_account_id: str,
) -> str | None:
    contact_id = upsert_contact_in_apollo(client, prospect)
    if not contact_id:
        return None
    try:
        time.sleep(1.2)
        client.add_to_sequence(contact_id, sequence_id, email_account_id)
        return contact_id
    except ApolloAPIError:
        return None


def enroll_batch(
    client: ApolloClient,
    prospects: list[Prospect],
    sequence_id: str,
    email_account_id: str,
    console: Console,
) -> dict[str, str | None]:
    results: dict[str, str | None] = {}
    for prospect in track(prospects, description="Enrolling in sequence...", console=console):
        key = prospect.email or prospect.full_name
        results[key] = enroll_contact(client, prospect, sequence_id, email_account_id)
        time.sleep(1.2)
    return results
