# Evaluations Avatar Prototype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an agent-only, stateless voice-to-avatar prototype that gets a mocked response from the backend and speaks it through HeyGen LiveAvatar.

**Architecture:** The browser uses speech recognition only to capture the agent's words. FastAPI exposes a HeyGen session-token endpoint and a message endpoint. The message endpoint invokes a one-node LangGraph whose node delegates to a function that selects from ten fixed responses. The React page owns the temporary conversation and LiveAvatar Web SDK lifecycle.

**Tech Stack:** React 19, TypeScript, Vite, Vitest, FastAPI, Pydantic, LangGraph, HTTPX, HeyGen LiveAvatar Web SDK.

**Spec:** Approved in chat on 2026-09-11.

## Global Constraints

- Evaluations must be visible and routable only in the agent workspace.
- No evaluation data is read from or written to PostgreSQL.
- The backend must never expose `HEYGEN_API_KEY` to the browser.
- The prototype response is randomly selected from exactly ten fixed responses.
- Graph definitions and graph-invoked functions must be in separate Python files.
- Speech recognition remains browser-only; typed input is a fallback.

---

### Task 1: Stateless evaluation backend contracts and graph

**Files:**
- Create: `backend/app/models/evaluations.py`
- Create: `backend/app/services/evaluations/evaluation_functions.py`
- Create: `backend/app/services/evaluations/evaluation_graph.py`
- Test: `backend/app/test/test_evaluations.py`

**Interfaces:**
- Produces `EvaluationMessageRequest`, `EvaluationMessageResponse`, `AvatarSessionResponse`.
- Produces `build_evaluation_graph()` and `evaluation_graph`.
- Produces `select_mock_response(message: str) -> str`.

- [ ] Write failing tests for random responses being selected from the ten-item catalog and the compiled graph returning a response.
- [ ] Run `pytest app/test/test_evaluations.py -q` from `backend/` and confirm it fails because the package is absent.
- [ ] Implement models, catalog-selection function, and `START -> generate_response -> END` graph.
- [ ] Run the focused backend test and confirm it passes.

### Task 2: HeyGen token service and API endpoints

**Files:**
- Create: `backend/app/services/evaluations/evaluation_service.py`
- Create: `backend/app/services/evaluations/__init__.py`
- Create: `backend/app/controllers/evaluations_controller.py`
- Modify: `backend/app/settings.py`
- Modify: `backend/app/main.py`
- Modify: `backend/requirements.txt`
- Modify: `docker-compose.yml`
- Test: `backend/app/test/test_evaluations.py`

**Interfaces:**
- Consumes `evaluation_graph` and Pydantic evaluation contracts.
- Produces `EvaluationService.create_avatar_session()` and `EvaluationService.respond()`.
- Produces `POST /api/v1/evaluations/avatar-session` and `POST /api/v1/evaluations/message`.

- [ ] Write failing endpoint tests for agent authorization, mocked message replies, and safely shaped HeyGen token results.
- [ ] Run the focused backend test and confirm it fails for the missing route/service.
- [ ] Implement settings, HTTPX-backed server-only HeyGen token request, typed service façade, controller, router registration, and Compose passthrough.
- [ ] Run the focused backend test and confirm it passes.

### Task 3: Agent evaluations page and avatar lifecycle

**Files:**
- Create: `frontend/src/features/evaluations/EvaluationsPage.tsx`
- Create: `frontend/src/features/evaluations/evaluations.test.tsx`
- Modify: `frontend/src/lib/navigation.ts`
- Modify: `frontend/src/app/router.tsx`
- Modify: `frontend/package.json`

**Interfaces:**
- Consumes `POST /api/v1/evaluations/avatar-session` and `POST /api/v1/evaluations/message`.
- Produces `/agent/evaluations` and agent-only navigation.
- Produces UI controls named “Start avatar”, “Speak”, and “End session”.

- [ ] Write failing UI tests for agent navigation, starting an avatar session, submitting a spoken/typed transcript, and displaying the reply.
- [ ] Run `npm test -- evaluations.test.tsx` from `frontend/` and confirm it fails because the page is absent.
- [ ] Install the official LiveAvatar SDK and implement the page’s session setup, stream attachment, stop cleanup, transcript controls, and text fallback.
- [ ] Run the focused frontend test and confirm it passes.

### Task 4: Verify prototype integration boundaries

**Files:**
- Modify: `README.md`

- [ ] Document the required HeyGen environment variables and browser requirements without adding secrets.
- [ ] Run the backend evaluation tests and full backend suite.
- [ ] Run the frontend evaluation tests, lint, and production build.
- [ ] Inspect the final diff to confirm no database module, migration, or secret file was introduced.
