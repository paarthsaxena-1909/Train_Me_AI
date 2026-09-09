# Agent Assignment Workflow Design

## Goal

Let an authenticated agent select a product lineup, create an assignment for
themselves, answer its generated questions in one frontend session, and submit
the complete response for mocked subjective evaluation.

## Ownership and lifecycle

An assignment is self-created by the current agent. Creation inserts the
assignment and its `assignment_agent_mapping` row atomically. The assignment
belongs to exactly one product lineup and is visible only to its mapped agent
through the agent workflow.

There is no draft concept, deadline, or partial-save operation. The database
status is `NULL` while an assignment is awaiting submission and `completed`
after successful evaluation. A completed assignment cannot be submitted or
Assignments remain in the agent's history; there is no assignment deletion workflow.

## Data model

`assignments` gains required `product_lineup_id` referencing
`product_lineups._id`; the unused deadline field is removed from the workflow.
`assignment_questions` removes `product_id`, adds generated `question` text,
and makes `answer` and `evaluation` nullable until the one-shot submission.
Assignment-level score and aggregate feedback columns are intentionally
deferred to a later schema change.
The mapping table receives a uniqueness constraint over `(assignment_id,
agent_id)`.

The mock generator builds stable questions from products and variants in the
selected lineup. The mock evaluator stores clearly labeled per-question
feedback and a subjective-evaluation caveat. Both are replaceable ports/adapters so real AI
can be introduced without changing the HTTP or persistence contracts.

## Backend API

All routes use the existing `/api/v1` prefix and bearer authentication.

- `GET /product-lineups` — list active selectable lineups with catalogue
  context needed by assignment generation.
- `POST /assignments` — accept `product_lineup_id`, create a self-assignment,
  generate mock questions, and return the assignment.
- `GET /assignments?product_lineup_id=...` — list the current agent's
  assignments, optionally filtered by lineup.
- `GET /assignments/{assignment_id}` — return questions and, when completed,
  per-question evaluation details for the mapped agent.
- `POST /assignments/{assignment_id}/submit` — accept every answer in one
  request, evaluate once, persist answers/feedback, and set `completed`.

Expected errors are `404` for missing/unowned resources, `409` for repeat
submission or deletion of a completed assignment, and `422` for malformed
payloads. Repository SQL remains one operation per readable SQL file, with
service transactions and typed Pydantic response models.

## Frontend

Add an agent-only Assignments navigation item and `/agent/assignments` route.
The page provides a lineup selector, assignment list, and create action. A
created assignment can be started in an in-memory answer form. The form sends
all answers only when submitted; it has no save button and does not call an
answer endpoint during editing.

After submission, the page renders the completed status, approximate score,
strengths, missing concepts, overall feedback, per-question feedback, and the
explicit subjective/mock limitation. Empty, loading, validation, and API
failure states are accessible and actionable. Deadline, draft, and partial
save controls are absent.

## Testing and documentation

Backend tests cover schema/migration shape, lineup selection, self-mapping,
mock generation, ownership, one-shot submission, completed status, evaluation
fields, and deletion rules. Frontend tests cover navigation, lineup selection,
creation, in-memory answering, one-request submission, evaluation rendering,
and the absence of draft/deadline controls.

Document the assignment service and separate Mermaid flows for creation,
submission/evaluation, and deletion. Mark mock generation and evaluation as
`PENDING AI REPLACEMENT` in docs and API-facing copy.

## Out of scope

- Real AI generation or evaluation.
- Assignment deadlines, drafts, multiple attempts, or partial saves.
- Admin assignment authoring or agent selection.
- Avatar/speech assignment modes.
