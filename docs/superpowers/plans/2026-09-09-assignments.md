# Agent Assignments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working agent-owned product-lineup assignment workflow with mocked question generation and subjective evaluation.

**Architecture:** Preserve the backend’s controller → service → repository → SQL-file flow. Assignments reference product lineups, mappings establish self-ownership, and generator/evaluator protocols isolate the mocked AI behavior. The frontend keeps answers in React state until one final submit request.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy metadata, Alembic, PostgreSQL SQL files, React 19, TypeScript, Vitest, Testing Library, Tailwind.

**Spec:** `docs/superpowers/specs/2026-09-09-assignments-design.md`

## Global Constraints

- All backend routes use `/api/v1` and authenticated agent role enforcement.
- Assignment status is `NULL` before submission and `completed` afterward; no draft/deadline/partial-save behavior.
- `assignment_questions` must not contain `product_id`; answers and evaluations are nullable until one-shot submission.
- Service methods use typed Pydantic response models and validate repository output at return boundaries.
- SQL stays in `backend/app/queries/postgres/<domain>/`, with service-owned transactions.
- Mock generation and evaluation must be visibly labeled `PENDING AI REPLACEMENT` in documentation and UI copy.
- Run focused tests after every task, then run the full backend/frontend verification suite before handoff.

## File Map

- Create `backend/database/versions/0005_assignments_lineup_workflow.py` for schema migration.
- Modify `backend/database/models/schema.py`, `backend/app/models/products.py`, and create `backend/app/models/assignments.py` for typed contracts.
- Create assignment SQL files and modify product SQL/repository/service only where lineup listing is needed.
- Create `backend/app/repositories/assignments_repository.py`, `backend/app/services/assignments/assignment_service.py`, `backend/app/services/assignments/assignment_generator_ai.py`, `backend/app/services/assignments/assignment_evaluator_ai.py`, and `backend/app/controllers/assignments_controller.py`.
- Create `backend/app/test/test_assignments.py` and update route/migration tests.
- Create `frontend/src/features/assignments/AssignmentsPage.tsx` and `frontend/src/features/assignments/assignments.test.tsx`; modify navigation, router, and icon support.
- Create `docs/services/assignments/README.md` and four Mermaid flow documents covering assignment creation, listing assignments, viewing one assignment, and the combined submission/evaluation flow.

### Task 1: Schema, migration, and typed assignment contracts

**Files:**
- Modify: `backend/database/models/schema.py`
- Create: `backend/database/versions/0005_assignments_lineup_workflow.py`
- Modify: `backend/app/models/products.py`
- Create: `backend/app/models/assignments.py`
- Test: `backend/app/test/test_assignments.py`, `backend/app/test/test_initial_migration.py`

**Interfaces:**
- Produces `ProductLineupResponse(id: int, lineup_identifier: str, product_count: int)`.
- Produces `AssignmentCreate(product_lineup_id: int)` and `AssignmentSubmit(answers: list[AssignmentAnswer])`.
- Produces `AssignmentResponse` with `id`, `product_lineup_id`, `lineup_identifier`, nullable `status`, question list, and optional evaluation summary.
- Produces `AssignmentQuestionResponse(id, question_number, question, answer, evaluation)` and `AssignmentEvaluationResponse(score, strengths, missing_concepts, overall_feedback, limitation)`.

- [ ] **Step 1: Write failing migration/model tests** asserting the assignment model has `product_lineup_id`, questions have `question` plus nullable `answer`/`evaluation`, questions do not have `product_id`, and the migration creates the lineup foreign key and mapping uniqueness.
- [ ] **Step 2: Run the focused tests**

Run: `cd backend && PYTHONPATH=. pytest -q app/test/test_assignments.py app/test/test_initial_migration.py`

Expected: FAIL because the new model fields, migration, and test file do not exist.

- [ ] **Step 3: Implement the SQLAlchemy model and Alembic migration**. Make the migration upgrade drop `assignment_questions.product_id` and `assignments.deadline`, add `assignments.product_lineup_id`, make question answer/evaluation nullable, add question text, and add the mapping unique constraint. Make downgrade restore the removed columns with safe defaults only where PostgreSQL requires them.
- [ ] **Step 4: Add Pydantic contracts** with bounds: lineup ID positive, answer text max 10000 characters, question count represented by generated data rather than a client-controlled field, and submit answers required for every returned question enforced in service logic.
- [ ] **Step 5: Run the focused tests** and confirm PASS, then run `python -m compileall app database`.
- [ ] **Step 6: Commit** with `git add backend/database backend/app/models backend/app/test && git commit -m "feat: add assignment lineup schema contracts"` (if repository metadata remains read-only, report that limitation and continue without commit).

### Task 2: Lineup and assignment backend workflow

**Files:**
- Create: `backend/app/queries/postgres/products/list_lineups.sql`
- Create: `backend/app/queries/postgres/assignments/create_assignment.sql`, `list_assignments.sql`, `get_assignment.sql`, `create_question.sql`, `submit_assignment.sql`
- Modify: `backend/app/repositories/products_repository.py`, `backend/app/services/products_service.py`, `backend/app/controllers/products_controller.py`
- Create: `backend/app/repositories/assignments_repository.py`, `backend/app/services/assignments/assignment_service.py`, `backend/app/services/assignments/assignment_generator_ai.py`, `backend/app/services/assignments/assignment_evaluator_ai.py`, `backend/app/controllers/assignments_controller.py`
- Modify: `backend/app/main.py`
- Test: `backend/app/test/test_assignments.py`, `backend/app/test/test_routes.py`

**Interfaces:**
- `ProductsRepository.list_lineups(session) -> rows` and `ProductsService.list_lineups(session) -> list[ProductLineupResponse]`.
- `AssignmentGenerator.generate(lineup_context) -> list[GeneratedQuestion]`.
- `AssignmentEvaluator.evaluate(questions_and_answers) -> AssignmentEvaluation`.
- `AssignmentsService.create(session, principal, payload) -> AssignmentResponse`.
- `AssignmentsService.list(session, principal, product_lineup_id | None) -> list[AssignmentSummaryResponse]`.
- `AssignmentsService.get(session, principal, assignment_id) -> AssignmentResponse`.
- `AssignmentsService.submit(session, principal, assignment_id, payload) -> AssignmentResponse`.

- [ ] **Step 1: Add failing service/controller tests** using lightweight fake session/repository objects. Cover deterministic placeholder generation, automatic mapping to `principal.account_id`, rejection of an unowned assignment, rejection of incomplete answer sets, completed status after submission, repeat submission `ConflictError`, completed deletion conflict, and route registration.
- [ ] **Step 2: Run the assignment tests**

Run: `cd backend && PYTHONPATH=. pytest -q app/test/test_assignments.py app/test/test_routes.py`

Expected: FAIL because lineup/assignment service, routes, and repository methods do not exist.

- [ ] **Step 3: Implement the mock AI protocols/adapters**. Generate 3–5 deterministic questions from lineup products/variants and include a source label. Evaluate each answer without external calls, returning an approximate score, strengths, missing concepts, overall feedback, and a limitation saying the evaluation is subjective/mock.
- [ ] **Step 4: Implement repository SQL boundaries**. Use a single transaction in the service: validate lineup, insert assignment, insert mapping, generate/insert questions, then commit. On submit, lock/read ownership and status, update every question answer/evaluation plus assignment evaluation fields/status, then commit. Never expose `product_id` in assignment query results.
- [ ] **Step 5: Implement the lineup endpoint and agent assignment controller** with `CurrentAgent`, typed response models, and query filtering. Return `404` for absent/unowned resources and `409` for repeat submit.
- [ ] **Step 6: Register routers and run focused tests** until PASS; run `cd backend && PYTHONPATH=. pytest -q` to catch regressions.
- [ ] **Step 7: Commit** with `git add backend/app backend/database/versions/0005_assignments_lineup_workflow.py && git commit -m "feat: add agent assignment workflow API"` (report if git metadata is unavailable).

### Task 3: Agent assignment UI

**Files:**
- Create: `frontend/src/features/assignments/AssignmentsPage.tsx`
- Create: `frontend/src/features/assignments/assignments.test.tsx`
- Modify: `frontend/src/lib/navigation.ts`, `frontend/src/app/router.tsx`, `frontend/src/components/Icon.tsx`

**Interfaces:**
- The page calls `GET /api/v1/product-lineups`, `GET /api/v1/assignments?product_lineup_id=<id>`, `POST /api/v1/assignments`, `GET /api/v1/assignments/<id>`, and `POST /api/v1/assignments/<id>/submit`.
- Answer payload is `{ answers: [{ question_id: number, answer: string }] }` and is created only by the submit handler from local React state.

- [ ] **Step 1: Write failing component tests** for agent nav/link, lineup selector, no-lineup empty state, create action, assignment list, start view, required answer fields, one submit API call containing all answers, completed evaluation rendering, and absence of “draft”, “deadline”, and “save” controls.
- [ ] **Step 2: Run the component tests**

Run: `cd frontend && npm test -- --run src/features/assignments/assignments.test.tsx src/app/router.test.tsx`

Expected: FAIL because the route, navigation item, page, and component do not exist.

- [ ] **Step 3: Add the assignment navigation item and route** for agents only; add a clipboard/check icon branch without changing existing icon behavior.
- [ ] **Step 4: Implement `AssignmentsPage`** with loading/error/empty states, lineup selection, create mutation, assignment list, start action, local answer map, disabled submit state, and evaluation result cards. Do not call an API on answer changes or unmount.
- [ ] **Step 5: Run the focused frontend tests** and confirm PASS.
- [ ] **Step 6: Run `cd frontend && npm run lint && npm run build` and fix only assignment-related type/lint/build issues.
- [ ] **Step 7: Commit** with `git add frontend/src && git commit -m "feat: add agent assignments workspace"` (report if git metadata is unavailable).

### Task 4: Service documentation and final verification

**Files:**
- Create: `docs/services/assignments/README.md`
- Create: `docs/services/assignments/flows/create-assignment.md`
- Create: `docs/services/assignments/flows/submit-assignment.md`
- Create: `docs/services/assignments/flows/view-assignments.md`
- Create: `docs/services/assignments/flows/view-assignment.md`
- Modify: `docs/README.md`, `README.md` if route/setup notes need an assignment entry

- [ ] **Step 1: Write documentation checks** in `backend/app/test/test_assignments.py` or a dedicated documentation test asserting all assignment flow files exist and contain `PENDING AI REPLACEMENT` where applicable, plus a route test asserting `/api/v1/product-lineups` and assignment routes are registered.
- [ ] **Step 2: Run the checks** and confirm they fail before documentation is written.
- [ ] **Step 3: Document implemented boundaries, route payloads, transaction behavior, no-draft/no-partial-save lifecycle, and the exact mock AI limitations. Add Mermaid sequence diagrams with implemented components and mock adapters labeled `PENDING AI REPLACEMENT`.
- [ ] **Step 4: Run the complete verification suite:**

```bash
docker compose config
cd backend && PYTHONPATH=. pytest -q
cd frontend && npm test -- --run
cd frontend && npm run lint
cd frontend && npm run build
```

- [ ] **Step 5: Inspect `git diff --check`, review the migration and route list, and verify no assignment question SQL/model contains `product_id` and no frontend assignment UI contains draft/deadline/save controls.**
- [ ] **Step 6: Commit documentation and tests** with `git add docs backend/app/test && git commit -m "docs: document assignment lifecycle and verification"` (report if git metadata remains read-only).

## Completion Checklist

- [ ] Product lineups are selectable by agents.
- [ ] Creation maps the assignment to the authenticated agent automatically.
- [ ] Questions map only to assignments and are mock-generated.
- [ ] Answers remain client-side until one complete submit.
- [ ] Submission evaluates once, stores completion and subjective feedback, and rejects repeats.
- [ ] Assignments remain available in the agent's assignment history; no delete route exists.
- [ ] Agent UI, tests, service docs, and Mermaid flows are present.
- [ ] Backend tests, frontend tests, lint, build, and compose config have fresh passing evidence.
