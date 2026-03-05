from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.deps import get_tenant_from_jwt
from db.client import supabase

router = APIRouter()


@router.get("/")
def list_contacts(tenant=Depends(get_tenant_from_jwt)):
    result = (
        supabase.table("contacts")
        .select("*")
        .eq("tenant_id", tenant["id"])
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{contact_id}")
def get_contact(contact_id: str, tenant=Depends(get_tenant_from_jwt)):
    result = (
        supabase.table("contacts")
        .select("*")
        .eq("id", contact_id)
        .eq("tenant_id", tenant["id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Contact not found")
    return result.data


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[dict] = None


@router.patch("/{contact_id}")
def update_contact(contact_id: str, body: ContactUpdate, tenant=Depends(get_tenant_from_jwt)):
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(400, "No fields to update")

    result = (
        supabase.table("contacts")
        .update(updates)
        .eq("id", contact_id)
        .eq("tenant_id", tenant["id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Contact not found")
    return result.data[0]
