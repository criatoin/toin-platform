from db.client import supabase
from typing import Optional


def save_lead(
    tenant_id: str,
    phone: str,
    name: Optional[str] = None,
    company: Optional[str] = None,
    objective: Optional[str] = None,
):
    metadata = {}
    if company:
        metadata["company"] = company
    if objective:
        metadata["objective"] = objective

    updates = {}
    if name:
        updates["name"] = name
    if metadata:
        updates["metadata"] = metadata

    if updates:
        supabase.table("contacts").update(updates).eq("tenant_id", tenant_id).eq(
            "phone", phone
        ).execute()
