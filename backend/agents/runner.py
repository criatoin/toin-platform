import asyncio
from agents.graphs.toin_graph import build_toin_graph
from agents.state import AgentState
from langchain_core.messages import HumanMessage, AIMessage
from services.whatsapp.adapter import WhatsAppAdapter
from db.client import supabase
from langfuse import Langfuse
from api.config import settings

graph = build_toin_graph()

_langfuse = None
if settings.langfuse_public_key and settings.langfuse_secret_key:
    _langfuse = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )


async def run_toin_agent(
    conversation: dict,
    message_text: str,
    tenant_id: str,
    adapter: WhatsAppAdapter,
    instance_name: str,
    from_phone: str,
):
    trace = _langfuse.trace(name="toin-agent", metadata={"tenant_id": tenant_id}) if _langfuse else None

    # Carrega histórico da conversa do banco (últimas 20 mensagens)
    msgs_result = (
        supabase.table("messages")
        .select("sender_type, content")
        .eq("conversation_id", conversation["id"])
        .order("created_at", desc=False)
        .limit(20)
        .execute()
    )

    history = []
    for msg in (msgs_result.data or []):
        if not msg.get("content"):
            continue
        if msg["sender_type"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        else:
            history.append(AIMessage(content=msg["content"]))

    # Adiciona mensagem atual
    history.append(HumanMessage(content=message_text))

    state: AgentState = {
        "messages": history,
        "tenant_id": tenant_id,
        "conversation_id": conversation["id"],
        "contact_phone": from_phone,
        "response_text": None,
        "handoff_triggered": False,
    }

    span = trace.span(name="graph-execution") if trace else None
    result = graph.invoke(state)
    if span:
        span.end()

    response_text = result.get("response_text") or ""

    if response_text:
        # Divide em partes para envio natural no WhatsApp
        # Quebra em \n\n (parágrafos) e \n (linhas)
        raw_parts: list[str] = []
        for para in response_text.split("\n\n"):
            for line in para.split("\n"):
                line = line.strip()
                if line:
                    raw_parts.append(line)
        parts = raw_parts if raw_parts else [response_text]

        for i, part in enumerate(parts):
            # Salva no DB primeiro
            supabase.table("messages").insert({
                "conversation_id": conversation["id"],
                "tenant_id": tenant_id,
                "sender_type": "bot",
                "content": part,
            }).execute()

            # Envia pelo WhatsApp
            try:
                await adapter.send_text(
                    instance=instance_name,
                    to=from_phone,
                    text=part,
                )
                # Pequena pausa entre mensagens para parecer mais natural
                if i < len(parts) - 1:
                    await asyncio.sleep(0.8)
            except Exception as e:
                print(f"[TOIN] Erro ao enviar mensagem para {from_phone}: {e}")

    # Handoff: desativa o bot na conversa
    if result.get("handoff_triggered"):
        supabase.table("conversations").update({"bot_active": False}).eq(
            "id", conversation["id"]
        ).execute()

    if trace:
        trace.update(output={"response": response_text})
    if _langfuse:
        _langfuse.flush()
