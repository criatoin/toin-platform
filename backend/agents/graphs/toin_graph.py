from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes.classify import classify_node
from agents.nodes.qualify_lead import qualify_lead_node
from agents.nodes.schedule import schedule_node
from agents.nodes.handoff import handoff_node


def build_toin_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_node)
    graph.add_node("qualify_lead", qualify_lead_node)
    graph.add_node("schedule", schedule_node)
    graph.add_node("handoff", handoff_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges("classify", route_after_classify, {
        "qualify": "qualify_lead",
        "schedule": "schedule",
        "handoff": "handoff",
        "done": END,
    })

    graph.add_edge("qualify_lead", END)
    graph.add_edge("schedule", END)
    graph.add_edge("handoff", END)

    return graph.compile()


def route_after_classify(state: AgentState) -> str:
    if state["handoff_triggered"]:
        return "handoff"
    stage = state["current_stage"]
    if stage in ("welcome", "qualify"):
        return "qualify"
    if stage == "schedule":
        return "schedule"
    return "done"
