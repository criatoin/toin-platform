from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from agents.state import AgentState
from agents.tools.crm_tool import save_lead
from api.config import settings
import json

llm = ChatOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0.3,
)


def qualify_lead_node(state: AgentState) -> AgentState:
    directive = open("directives/toin.md").read()

    system = f"""
{directive}

Dados ja coletados:
- Nome: {state.get('lead_name') or 'nao informado'}
- Empresa: {state.get('lead_company') or 'nao informado'}
- Objetivo: {state.get('lead_objective') or 'nao informado'}

Se faltam dados, faca UMA pergunta por vez para coletar.
Se todos os dados foram coletados, avance para proposta e agendamento.

Responda em JSON:
{{
  "response": "texto da sua resposta",
  "lead_name": "nome se mencionado ou null",
  "lead_company": "empresa se mencionada ou null",
  "lead_objective": "objetivo se mencionado ou null",
  "advance_to_schedule": false
}}
"""
    result = llm.invoke([
        SystemMessage(content=system),
        *state["messages"],
    ])

    try:
        parsed = json.loads(result.content)
    except Exception:
        parsed = {"response": result.content, "advance_to_schedule": False}

    updates = {
        "response_text": parsed.get("response", ""),
        "current_stage": "schedule" if parsed.get("advance_to_schedule") else state.get("current_stage", "qualify"),
    }

    for field in ["lead_name", "lead_company", "lead_objective"]:
        if parsed.get(field):
            updates[field] = parsed[field]

    if any(updates.get(f) for f in ["lead_name", "lead_company", "lead_objective"]):
        save_lead(
            tenant_id=state["tenant_id"],
            phone=state["contact_phone"],
            name=updates.get("lead_name") or state.get("lead_name"),
            company=updates.get("lead_company") or state.get("lead_company"),
            objective=updates.get("lead_objective") or state.get("lead_objective"),
        )

    return {
        **state,
        **updates,
        "messages": [*state["messages"], AIMessage(content=updates["response_text"])],
    }
