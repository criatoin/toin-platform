from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.toin_agent import toin_agent_node
from agents.nodes.handoff import handoff_node


def _route(state: AgentState) -> str:
    return "handoff" if state["handoff_triggered"] else END


def build_toin_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("toin_agent", toin_agent_node)
    graph.add_node("handoff", handoff_node)

    graph.set_entry_point("toin_agent")

    graph.add_conditional_edges("toin_agent", _route, {
        "handoff": "handoff",
        END: END,
    })

    graph.add_edge("handoff", END)

    return graph.compile()
