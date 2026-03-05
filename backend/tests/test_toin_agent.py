import pytest
from agents.graphs.toin_graph import build_toin_graph, route_after_classify
from agents.state import AgentState
from langchain_core.messages import HumanMessage


@pytest.fixture
def base_state() -> AgentState:
    return {
        "messages": [HumanMessage(content="Ola, quero saber mais sobre voces")],
        "tenant_id": "test-tenant",
        "conversation_id": "test-conv",
        "contact_phone": "+5511999999999",
        "lead_name": None,
        "lead_company": None,
        "lead_objective": None,
        "lead_email": None,
        "current_stage": "welcome",
        "handoff_triggered": False,
        "response_text": None,
    }


def test_graph_builds():
    graph = build_toin_graph()
    assert graph is not None


def test_handoff_route():
    """Garante que handoff_triggered=True leva ao no de handoff."""
    state = {"current_stage": "qualify", "handoff_triggered": True}
    assert route_after_classify(state) == "handoff"


def test_qualify_route_from_welcome():
    state = {"current_stage": "welcome", "handoff_triggered": False}
    assert route_after_classify(state) == "qualify"


def test_qualify_route_from_qualify():
    state = {"current_stage": "qualify", "handoff_triggered": False}
    assert route_after_classify(state) == "qualify"


def test_schedule_route():
    state = {"current_stage": "schedule", "handoff_triggered": False}
    assert route_after_classify(state) == "schedule"


def test_done_route():
    state = {"current_stage": "done", "handoff_triggered": False}
    assert route_after_classify(state) == "done"
