# Assignments service

Agents select an active product lineup and create an assignment for themselves.
Creation inserts the assignment, the `assignment_agent_mapping` ownership row,
and generated questions in one service transaction. Questions belong only to
the assignment; they do not reference individual products.

An assignment has no deadline, draft, or partial-save state. Answers stay in
the frontend session until `POST /api/v1/assignments/{id}/submit` receives the
complete set. The service evaluates once, stores per-question feedback and an
per-question feedback, and changes status from `NULL` to `completed`. Assignment-level scoring and aggregate feedback are intentionally deferred.

## Routes

- `GET /api/v1/product-lineups`
- `POST /api/v1/assignments` with `{ "product_lineup_id": 1 }`
- `GET /api/v1/assignments?product_lineup_id=1`
- `GET /api/v1/assignments/{assignment_id}`
- `POST /api/v1/assignments/{assignment_id}/submit` with an `answers` array
- There is no assignment deletion route; assignments remain part of the agent's history.

`MockAssignmentGenerator` and `MockAssignmentEvaluator` are explicit
`PENDING AI REPLACEMENT` adapters. The evaluator currently returns feedback for
each question only; assignment-level scoring, strengths, missing concepts, and
overall feedback will be added in a later schema change. The feedback is
subjective and mock-generated rather than an objective grade.
