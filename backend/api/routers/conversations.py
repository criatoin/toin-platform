from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import get_tenant_from_jwt
from db.client import supabase

router = APIRouter()


@router.get("/")
def list_conversations(tenant=Depends(get_tenant_from_jwt)):
    result = (
        supabase.table("conversations")
        .select("*, contacts(name, phone), messages(content, created_at, sender_type)")
        .eq("tenant_id", tenant["id"])
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str, tenant=Depends(get_tenant_from_jwt)):
    result = (
        supabase.table("conversations")
        .select("*, contacts(*), messages(*)")
        .eq("id", conversation_id)
        .eq("tenant_id", tenant["id"])
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Conversation not found")
    return result.data


class BotToggle(BaseModel):
    bot_active: bool


@router.patch("/{conversation_id}/bot")
def toggle_bot(conversation_id: str, body: BotToggle, tenant=Depends(get_tenant_from_jwt)):
    result = (
        supabase.table("conversations")
        .update({"bot_active": body.bot_active})
        .eq("id", conversation_id)
        .eq("tenant_id", tenant["id"])
        .execute()
    )
    if not result.data:
        raise HTTPException(404, "Conversation not found")
    return result.data[0]
