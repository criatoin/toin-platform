from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from agents.state import AgentState
from agents.tools.calendar_tool import check_availability, create_event
from api.config import settings

llm = ChatOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0.5,
)

HANDOFF_KEYWORDS = [
    "falar com pessoa",
    "falar com alguem",
    "falar com alguém",
    "atendente humano",
    "quero um humano",
    "preciso de um atendente",
    "falar com especialista",
    "falar com humano",
    "quero falar com",
    "me passa para",
]


@tool
def verificar_disponibilidade() -> str:
    """Consulta os horários disponíveis no Google Calendar para agendar uma reunião de demonstração da TOIN. Use quando o cliente quiser agendar."""
    return check_availability(days_ahead=7)


@tool
def agendar_reuniao(start_iso: str, lead_name: str, lead_email: str, lead_phone: str = "") -> str:
    """Cria evento no Google Calendar. Use quando o cliente confirmar o horário e informar o e-mail.
    start_iso: datetime no formato ISO 8601, ex: 2026-03-15T14:00:00
    lead_name: nome do cliente
    lead_email: e-mail do cliente para envio do convite
    lead_phone: telefone do cliente (opcional)
    """
    return create_event(start_iso, lead_name, lead_email, lead_phone)


TOOLS = [verificar_disponibilidade, agendar_reuniao]
llm_with_tools = llm.bind_tools(TOOLS)
tools_map = {t.name: t for t in TOOLS}


def toin_agent_node(state: AgentState) -> AgentState:
    directive = open("directives/toin.md").read()

    last_msg = state["messages"][-1].content.lower() if state["messages"] else ""

    # Verifica handoff
    if any(kw in last_msg for kw in HANDOFF_KEYWORDS):
        return {
            **state,
            "response_text": "Vou conectar você com um especialista da nossa equipe. Em breve alguém entrará em contato! 😊",
            "handoff_triggered": True,
        }

    messages = [SystemMessage(content=directive), *state["messages"]]
    result = llm_with_tools.invoke(messages)

    # Executa ferramentas se chamadas
    if hasattr(result, "tool_calls") and result.tool_calls:
        messages = [*messages, result]
        for tc in result.tool_calls:
            fn = tools_map.get(tc["name"])
            if fn:
                try:
                    output = fn.invoke(tc["args"])
                except Exception as e:
                    output = f"Erro ao acessar calendário: {e}"
                messages.append(ToolMessage(content=str(output), tool_call_id=tc["id"]))
        # Gera resposta final com resultado das ferramentas
        result = llm_with_tools.invoke(messages)

    response = (result.content or "").strip()

    return {
        **state,
        "response_text": response,
        "handoff_triggered": False,
        "messages": [*state["messages"], AIMessage(content=response)],
    }
