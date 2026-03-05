from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: List[BaseMessage]
    tenant_id: str
    conversation_id: str
    contact_phone: str
    # Dados coletados durante o fluxo
    lead_name: Optional[str]
    lead_company: Optional[str]
    lead_objective: Optional[str]
    lead_email: Optional[str]
    # Controle de fluxo
    current_stage: str       # 'welcome', 'qualify', 'propose', 'schedule', 'done'
    handoff_triggered: bool
    # Resposta para enviar ao usuario
    response_text: Optional[str]
