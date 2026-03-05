from fastapi import APIRouter, BackgroundTasks, Request, HTTPException, Depends
from pydantic import BaseModel
from api.deps import require_service_token
from api.config import settings
from services.whatsapp.evolution import EvolutionAdapter, normalize_evolution_event
from db.client import supabase

router = APIRouter()


def get_evolution_adapter() -> EvolutionAdapter:
    return EvolutionAdapter(
        base_url=settings.evolution_api_url,
        api_key=settings.evolution_api_key,
    )


# --- Webhook (publico — validado por HMAC ou IP whitelist em producao) ---
@router.post("/webhook/{instance_name}")
async def webhook(instance_name: str, request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    normalized = normalize_evolution_event(payload)
    if normalized is None:
        return {"status": "ignored"}

    background_tasks.add_task(handle_incoming_message, normalized)
    return {"status": "queued"}


async def handle_incoming_message(msg: dict):
    """
    1. Encontra instancia WhatsApp no banco pelo instance_name
    2. Upsert contact
    3. Upsert/cria conversation
    4. Salva mensagem
    5. Se bot_active, dispara agente
    """
    from agents.runner import run_toin_agent

    inst = (
        supabase.table("whatsapp_instances")
        .select("*")
        .eq("instance_name", msg["instance_name"])
        .single()
        .execute()
    )
    if not inst.data:
        return

    tenant_id = inst.data["tenant_id"]
    instance_id = inst.data["id"]

    # Upsert contact
    contact = supabase.table("contacts").upsert(
        {"tenant_id": tenant_id, "phone": msg["from_phone"]},
        on_conflict="tenant_id,phone",
    ).execute()
    contact_id = contact.data[0]["id"]

    # Encontra ou cria conversation aberta
    conv = (
        supabase.table("conversations")
        .select("*")
        .eq("tenant_id", tenant_id)
        .eq("contact_id", contact_id)
        .eq("status", "open")
        .maybe_single()
        .execute()
    )

    if conv.data:
        conversation = conv.data
    else:
        agent = (
            supabase.table("agents")
            .select("id")
            .eq("tenant_id", tenant_id)
            .limit(1)
            .execute()
        )
        agent_id = agent.data[0]["id"] if agent.data else None
        new_conv = supabase.table("conversations").insert({
            "tenant_id": tenant_id,
            "contact_id": contact_id,
            "whatsapp_instance_id": instance_id,
            "agent_id": agent_id,
            "bot_active": True,
        }).execute()
        conversation = new_conv.data[0]

    # Salva mensagem
    supabase.table("messages").insert({
        "conversation_id": conversation["id"],
        "tenant_id": tenant_id,
        "sender_type": "user",
        "content": msg.get("text") or "",
        "media_type": msg.get("media_type"),
        "whatsapp_message_id": msg["raw_message_id"],
    }).execute()

    # Dispara agente se bot ativo
    if conversation["bot_active"] and msg.get("text"):
        await run_toin_agent(
            conversation=conversation,
            message_text=msg["text"],
            tenant_id=tenant_id,
            adapter=get_evolution_adapter(),
            instance_name=msg["instance_name"],
            from_phone=msg["from_phone"],
        )


# --- Gestao de instancias ---
class InstanceCreate(BaseModel):
    tenant_id: str
    instance_name: str


@router.post("/instances", status_code=201, dependencies=[Depends(require_service_token)])
async def create_instance(body: InstanceCreate):
    adapter = get_evolution_adapter()
    result = await adapter.create_instance(body.instance_name)

    db_result = supabase.table("whatsapp_instances").insert({
        "tenant_id": body.tenant_id,
        "instance_name": body.instance_name,
        "status": "qr_pending",
    }).execute()
    return {"db": db_result.data[0], "provider": result}


@router.get("/instances/{instance_id}/qrcode", dependencies=[Depends(require_service_token)])
async def get_qrcode(instance_id: str):
    inst = (
        supabase.table("whatsapp_instances")
        .select("instance_name")
        .eq("id", instance_id)
        .single()
        .execute()
    )
    if not inst.data:
        raise HTTPException(404, "Instance not found")
    adapter = get_evolution_adapter()
    qr = await adapter.get_qrcode(inst.data["instance_name"])
    return {"qrcode_base64": qr}


@router.post("/instances/{instance_id}/reconnect", dependencies=[Depends(require_service_token)])
async def reconnect_instance(instance_id: str):
    inst = (
        supabase.table("whatsapp_instances")
        .select("instance_name")
        .eq("id", instance_id)
        .single()
        .execute()
    )
    if not inst.data:
        raise HTTPException(404, "Instance not found")
    adapter = get_evolution_adapter()
    result = await adapter.reconnect(inst.data["instance_name"])
    return result
