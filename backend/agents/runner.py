from agents.graphs.toin_graph import build_toin_graph
from agents.state import AgentState
from langchain_core.messages import HumanMessage
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

    saved_state = conversation.get("agent_state") or {}

    state: AgentState = {
        "messages": [HumanMessage(content=message_text)],
        "tenant_id": tenant_id,
        "conversation_id": conversation["id"],
        "contact_phone": from_phone,
        "lead_name": saved_state.get("lead_name"),
        "lead_company": saved_state.get("lead_company"),
        "lead_objective": saved_state.get("lead_objective"),
        "lead_email": saved_state.get("lead_email"),
        "current_stage": saved_state.get("current_stage", "welcome"),
        "handoff_triggered": False,
        "response_text": None,
    }

    span = trace.span(name="graph-execution") if trace else None
    result = graph.invoke(state)
    if span:
        span.end()

    # Persiste estado atualizado na conversa (updated_at é gerenciado pelo trigger do DB)
    supabase.table("conversations").update({
        "agent_state": {
            "lead_name": result.get("lead_name"),
            "lead_company": result.get("lead_company"),
            "lead_objective": result.get("lead_objective"),
            "lead_email": result.get("lead_email"),
            "current_stage": result.get("current_stage"),
        },
    }).eq("id", conversation["id"]).execute()

    # Envia resposta via WhatsApp
    if result.get("response_text"):
        await adapter.send_text(
            instance=instance_name,
            to=from_phone,
            text=result["response_text"],
        )

        supabase.table("messages").insert({
            "conversation_id": conversation["id"],
            "tenant_id": tenant_id,
            "sender_type": "bot",
            "content": result["response_text"],
        }).execute()

    if trace:
        trace.update(output={"response": result.get("response_text")})
    if _langfuse:
        _langfuse.flush()
