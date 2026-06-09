from __future__ import annotations
from rich.console import Console
from rich.progress import track
from ..models import Prospect, SyncResult

try:
    from hubspot import HubSpot
    from hubspot.crm.contacts.models import SimplePublicObjectInputForCreate as ContactInput
    from hubspot.crm.deals.models import SimplePublicObjectInputForCreate as DealInput
    from hubspot.crm.associations.v4.models import AssociationSpec
    _HUBSPOT_OK = True
except ImportError:
    _HUBSPOT_OK = False


def build_hubspot_client(access_token: str):
    if not _HUBSPOT_OK:
        raise ImportError("hubspot-api-client not installed. Run: pip install hubspot-api-client")
    return HubSpot(access_token=access_token)


def upsert_contact(hs, prospect: Prospect) -> str | None:
    props: dict = {
        "email": prospect.email or "",
        "firstname": prospect.first_name,
        "lastname": prospect.last_name,
    }
    if prospect.title:
        props["jobtitle"] = prospect.title
    if prospect.company:
        props["company"] = prospect.company
    if prospect.linkedin_url:
        props["hs_linkedin_bio"] = prospect.linkedin_url
    if prospect.employee_count:
        props["numemployees"] = str(prospect.employee_count)
    if prospect.industry:
        props["industry"] = prospect.industry

    try:
        result = hs.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=ContactInput(properties=props)
        )
        return result.id
    except Exception as exc:
        exc_str = str(exc)
        if "409" in exc_str or "CONTACT_EXISTS" in exc_str:
            return _find_contact_by_email(hs, prospect.email or "")
        return None


def _find_contact_by_email(hs, email: str) -> str | None:
    try:
        from hubspot.crm.contacts.models import PublicObjectSearchRequest
        req = PublicObjectSearchRequest(
            filter_groups=[{
                "filters": [{"propertyName": "email", "operator": "EQ", "value": email}]
            }],
            limit=1,
        )
        results = hs.crm.contacts.search_api.do_search(public_object_search_request=req)
        if results.results:
            return results.results[0].id
    except Exception:
        pass
    return None


def create_deal(hs, prospect: Prospect, contact_id: str, pipeline_id: str) -> str | None:
    deal_name = f"{prospect.company or prospect.full_name} - CaseInsight Outreach"
    try:
        deal = hs.crm.deals.basic_api.create(
            simple_public_object_input_for_create=DealInput(properties={
                "dealname": deal_name,
                "pipeline": pipeline_id,
                "dealstage": "appointmentscheduled",
            })
        )
        hs.crm.deals.associations_api.create(
            deal_id=deal.id,
            to_object_type="contacts",
            to_object_id=contact_id,
            association_spec=[
                AssociationSpec(
                    association_category="HUBSPOT_DEFINED",
                    association_type_id=3,
                )
            ],
        )
        return deal.id
    except Exception:
        return None


def sync_prospect(
    hs,
    prospect: Prospect,
    pipeline_id: str,
    with_deal: bool = True,
) -> SyncResult:
    result = SyncResult(prospect_email=prospect.email or prospect.full_name)
    contact_id = upsert_contact(hs, prospect)
    if not contact_id:
        result.errors.append("Failed to upsert HubSpot contact")
        return result
    result.hubspot_contact_id = contact_id
    if with_deal and pipeline_id:
        deal_id = create_deal(hs, prospect, contact_id, pipeline_id)
        result.hubspot_deal_id = deal_id
        if not deal_id:
            result.errors.append("Failed to create HubSpot deal")
    return result


def sync_batch(
    hs,
    prospects: list[Prospect],
    pipeline_id: str,
    console: Console,
    with_deal: bool = True,
) -> list[SyncResult]:
    results = []
    for prospect in track(prospects, description="Syncing to HubSpot...", console=console):
        results.append(sync_prospect(hs, prospect, pipeline_id, with_deal=with_deal))
    return results
