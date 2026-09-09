"""Assignment question-generation providers."""

from typing import Protocol

from app.models.assignments import GeneratedQuestion


class AssignmentGenerator(Protocol):
    def generate(self, context: list[dict]) -> list[GeneratedQuestion]: ...


class MockAssignmentGenerator:
    """Deterministic ten-question provider pending the real AI integration."""

    def generate(self, context: list[dict]) -> list[GeneratedQuestion]:
        lineup = context[0] if context else {"lineup_identifier": "selected lineup"}
        name = lineup.get("lineup_identifier", "selected lineup")
        prompts = [
            f"What is the main value proposition of the {name} lineup?",
            f"Which product or variant in {name} best fits a customer need, and why?",
            f"What important specification should an agent explain for {name}?",
            f"How would you introduce the {name} lineup to a new customer?",
            f"What customer question should you ask before recommending {name}?",
            f"What is one differentiator between products in {name}?",
            f"How should an agent explain the main benefit of {name} simply?",
            f"Which product detail in {name} needs careful explanation?",
            f"What objection might a customer raise about {name}, and how would you respond?",
            f"Summarize the key learning point for the {name} lineup.",
        ]
        return [
            GeneratedQuestion(question_number=index, question=question)
            for index, question in enumerate(prompts, 1)
        ]
