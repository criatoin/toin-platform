from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import AgentState
from api.config import settings
import json

llm = ChatOpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1",
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0,
)

CLASSIFY_PROMPT = """
Analise a ultima mensagem do usuario e o estado atual da conversa.
Retorne um JSON com:
- "intent": uma de ["greeting", "provide_info", "request_schedule", "request_human", "question", "other"]
- "handoff_needed": true/false
- "next_stage": uma de ["welcome", "qualify", "propose", "schedule", "done"]

Estado atual: {current_stage}
Dados coletados: nome={lead_name}, empresa={lead_company}, objetivo={lead_objective}

Responda APENAS com JSON valido.
"""


def classify_node(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content if state["messages"] else ""

    prompt = CLASSIFY_PROMPT.format(
        current_stage=state.get("current_stage", "welcome"),
        lead_name=state.get("lead_name"),
        lead_company=state.get("lead_company"),
        lead_objective=state.get("lead_objective"),
    )

    result = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Ultima mensagem: {last_msg}"),
    ])

    try:
        parsed = json.loads(result.content)
    except Exception:
        parsed = {
            "intent": "other",
            "handoff_needed": False,
            "next_stage": state.get("current_stage", "qualify"),
        }

    return {
        **state,
        "current_stage": parsed.get("next_stage", state.get("current_stage", "qualify")),
        "handoff_triggered": parsed.get("handoff_needed", False),
    }
