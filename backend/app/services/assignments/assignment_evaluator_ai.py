"""Assignment question-evaluation providers."""

from typing import Protocol


class AssignmentEvaluator(Protocol):
    def evaluate(self, questions: list[dict]) -> dict[int, str]: ...


class MockAssignmentEvaluator:
    def evaluate(self, questions: list[dict]) -> dict[int, str]:
        return {
            item["id"]: "Mock evaluation: answer received; nuanced subjective feedback is pending AI replacement."
            for item in questions
        }
