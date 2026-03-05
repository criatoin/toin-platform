from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, AIMessage
from agents.state import AgentState
from agents.tools.calendar_tool import check_availability, create_event
from api.config import settings
import json

llm = ChatGroq(api_key=settings.groq_api_key, model="llama-3.3-70b-versatile", temperature=0.2)


def schedule_node(state: AgentState) -> AgentState:
    directive = open("directives/toin.md").read()

    slots = check_availability(days_ahead=7, duration_minutes=30)
    slots_text = "\n".join([f"- {s}" for s in slots[:5]])

    system = f"""
{directive}

Voce esta na etapa de agendamento.
Horarios disponiveis nos proximos 7 dias:
{slots_text}

Apresente no maximo 2 opcoes ao usuario de forma amigavel.
Se o usuario ja escolheu um horario e forneceu e-mail, crie o evento.

Responda em JSON:
{{
  "response": "texto da resposta",
  "should_create_event": false,
  "chosen_slot": null,
  "lead_email": null
}}
"""

    result = llm.invoke([SystemMessage(content=system), *state["messages"]])

    try:
        parsed = json.loads(result.content)
    except Exception:
        parsed = {"response": result.content, "should_create_event": False}

    updates = {"response_text": parsed.get("response", "")}

    if parsed.get("should_create_event") and parsed.get("chosen_slot") and parsed.get("lead_email"):
        create_event(
            tenant_id=state["tenant_id"],
            slot=parsed["chosen_slot"],
            lead_name=state.get("lead_name") or "Lead",
            lead_email=parsed["lead_email"],
            lead_phone=state["contact_phone"],
        )
        updates["lead_email"] = parsed["lead_email"]
        updates["current_stage"] = "done"

    return {
        **state,
        **updates,
        "messages": [*state["messages"], AIMessage(content=updates["response_text"])],
    }
