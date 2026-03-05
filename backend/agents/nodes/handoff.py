from agents.state import AgentState
from db.client import supabase


def handoff_node(state: AgentState) -> AgentState:
    """Desativa o bot e notifica atendentes via DB."""
    supabase.table("conversations").update({"bot_active": False}).eq(
        "id", state["conversation_id"]
    ).execute()

    response = "Vou conectar voce com um especialista da nossa equipe. Em breve alguem entrara em contato."

    return {**state, "response_text": response, "handoff_triggered": True}
