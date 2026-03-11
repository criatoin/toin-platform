from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]      # Histórico completo da conversa
    tenant_id: str
    conversation_id: str
    contact_phone: str
    response_text: Optional[str]     # Resposta gerada (pode conter \n\n para múltiplas mensagens)
    handoff_triggered: bool
