from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from agents.state import AgentState
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


def toin_agent_node(state: AgentState) -> AgentState:
    directive = open("directives/toin.md").read()

    last_msg = state["messages"][-1].content.lower() if state["messages"] else ""

    # Verifica se cliente quer handoff
    if any(kw in last_msg for kw in HANDOFF_KEYWORDS):
        return {
            **state,
            "response_text": "Vou conectar você com um especialista da nossa equipe. Em breve alguém entrará em contato! 😊",
            "handoff_triggered": True,
        }

    result = llm.invoke([
        SystemMessage(content=directive),
        *state["messages"],
    ])

    response = result.content.strip()

    return {
        **state,
        "response_text": response,
        "handoff_triggered": False,
        "messages": [*state["messages"], AIMessage(content=response)],
    }
