"""LangGraph definition for the stateless evaluation-avatar prototype."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.services.evaluations.evaluation_functions import select_mock_response


class EvaluationState(TypedDict, total=False):
    message: str
    response_text: str


def generate_response(state: EvaluationState) -> EvaluationState:
    """Delegate response generation to the independently testable function module."""
    return {"response_text": select_mock_response(state["message"])}


def build_evaluation_graph():
    workflow = StateGraph(EvaluationState)
    workflow.add_node("generate_response", generate_response)
    workflow.add_edge(START, "generate_response")
    workflow.add_edge("generate_response", END)
    return workflow.compile()


evaluation_graph = build_evaluation_graph()
