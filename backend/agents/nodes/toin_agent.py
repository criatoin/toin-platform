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
def verificar_disponibilidade(dia_preferido: str, horario_preferido: str) -> str:
    """
    Verifica se o dia e horário preferidos pelo cliente estão disponíveis no calendário.

    PRÉ-CONDIÇÃO OBRIGATÓRIA: só chame esta ferramenta APÓS o cliente ter informado
    explicitamente o dia preferido E o horário preferido na conversa.

    dia_preferido: dia que o cliente mencionou, ex: "segunda", "15/03", "amanhã"
    horario_preferido: horário que o cliente mencionou, ex: "14h", "10:00", "manhã"
    """
    return check_availability(days_ahead=7)


@tool
def agendar_reuniao(start_iso: str, lead_name: str, lead_email: str, lead_phone: str = "") -> str:
    """
    Cria a reunião de demonstração no Google Calendar.

    PRÉ-CONDIÇÃO OBRIGATÓRIA: só chame esta ferramenta APÓS:
    1. O cliente ter confirmado o dia e horário específico
    2. O cliente ter fornecido o e-mail
    3. O cliente ter confirmado que quer agendar

    start_iso: data e hora no formato ISO 8601 BASEADO no que o cliente confirmou,
               ex: "2026-03-15T14:00:00" — NUNCA invente a data, use o que o cliente disse.
    lead_name: nome do cliente coletado na conversa
    lead_email: e-mail fornecido pelo cliente
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
