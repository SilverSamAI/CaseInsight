from __future__ import annotations
import time
import requests
from ..utils.retry import with_retry


class ApolloAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ApolloRateLimitError(ApolloAPIError):
    """Raised on 429 or 5xx responses — safe to retry."""


class ApolloClient:
    BASE = "https://api.apollo.io/v1"

    def __init__(self, api_key: str):
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": api_key,
        })

    def search_people(
        self,
        titles: list[str],
        company_names: list[str] | None = None,
        industries: list[str] | None = None,
        employee_ranges: list[str] | None = None,
        page: int = 1,
        per_page: int = 25,
    ) -> dict:
        payload: dict = {"person_titles": titles, "page": page, "per_page": per_page}
        if company_names:
            payload["organization_names"] = company_names
        if industries:
            payload["organization_industry_tag_ids"] = industries
        if employee_ranges:
            payload["organization_num_employees_ranges"] = employee_ranges
        return self._post("/mixed_people/search", payload)

    def enrich_person(
        self,
        email: str | None = None,
        linkedin_url: str | None = None,
    ) -> dict:
        if not email and not linkedin_url:
            raise ValueError("Either email or linkedin_url required")
        payload = {}
        if email:
            payload["email"] = email
        if linkedin_url:
            payload["linkedin_url"] = linkedin_url
        return self._post("/people/match", payload)

    def enrich_organization(self, domain: str) -> dict:
        return self._get("/organizations/enrich", {"domain": domain})

    def add_to_sequence(
        self,
        contact_id: str,
        sequence_id: str,
        email_account_id: str,
    ) -> dict:
        return self._post(
            f"/emailer_campaigns/{sequence_id}/add_contact_ids",
            {
                "contact_ids": [contact_id],
                "emailer_schedule_id": None,
                "send_email_from_email_account_id": email_account_id,
            },
        )

    def create_contact(self, data: dict) -> dict:
        return self._post("/contacts", data)

    def search_contacts_by_email(self, email: str) -> dict:
        return self._post("/contacts/search", {"q_keywords": email, "page": 1, "per_page": 1})

    @with_retry(retry_on=(ApolloRateLimitError, requests.ConnectionError, requests.Timeout))
    def _get(self, path: str, params: dict | None = None) -> dict:
        resp = self._session.get(f"{self.BASE}{path}", params=params)
        self._raise_for_status(resp)
        return resp.json()

    @with_retry(retry_on=(ApolloRateLimitError, requests.ConnectionError, requests.Timeout))
    def _post(self, path: str, payload: dict) -> dict:
        resp = self._session.post(f"{self.BASE}{path}", json=payload)
        self._raise_for_status(resp)
        return resp.json()

    @staticmethod
    def _raise_for_status(resp: requests.Response) -> None:
        if resp.ok:
            return
        msg = f"Apollo {resp.status_code}: {resp.text[:400]}"
        if resp.status_code == 429 or resp.status_code >= 500:
            raise ApolloRateLimitError(msg, status_code=resp.status_code)
        raise ApolloAPIError(msg, status_code=resp.status_code)
