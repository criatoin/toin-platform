from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import get_tenant_from_jwt
from api.config import settings
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


class MessageCreate(BaseModel):
    content: str


@router.post("/{conversation_id}/messages", status_code=201)
async def send_message(conversation_id: str, body: MessageCreate, tenant=Depends(get_tenant_from_jwt)):
    """Envia mensagem como agente humano — salva no DB e envia via WhatsApp."""
    conv = (
        supabase.table("conversations")
        .select("*, contacts(phone), whatsapp_instances(instance_name)")
        .eq("id", conversation_id)
        .eq("tenant_id", tenant["id"])
        .single()
        .execute()
    )
    if not conv.data:
        raise HTTPException(404, "Conversation not found")

    conv_data = conv.data
    phone = (conv_data.get("contacts") or {}).get("phone")
    instance_name = (conv_data.get("whatsapp_instances") or {}).get("instance_name")

    msg = supabase.table("messages").insert({
        "conversation_id": conversation_id,
        "tenant_id": tenant["id"],
        "sender_type": "human_agent",
        "content": body.content,
    }).execute()

    if instance_name and phone:
        from services.whatsapp.evolution import EvolutionAdapter
        adapter = EvolutionAdapter(settings.evolution_api_url, settings.evolution_api_key)
        try:
            await adapter.send_text(instance=instance_name, to=phone, text=body.content)
        except Exception as e:
            print(f"[TOIN] Erro ao enviar mensagem humana: {e}")

    return msg.data[0]
