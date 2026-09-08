# Train Me CRUD Epic Design

## Goal

Build the current Train Me application as a complete, role-aware CRUD system.
Agents and administrators can register and authenticate, administrators manage
the product catalogue and create assessments, and agents use product Q&A,
assignments, and daily face attendance. AI-backed behavior is represented only
by explicit, deterministic placeholder adapters that can later be replaced.

## Delivery strategy

Deliver one vertical slice end to end before starting the next:

1. Shared application foundation and orchestration boundary.
2. Authentication.
3. Product catalogue.
4. Knowledge assignments.
5. Product Q&A.
6. Daily face attendance.
7. Whole-stack integration and documentation audit.

Each slice includes schema/migration changes, controllers, services,
repositories, SQL files, frontend UI, tests, service documentation, and a
Mermaid sequence diagram when the flow has multiple steps.

## Architectural boundaries

The existing backend convention remains the default:

```text
controller -> service -> repository -> one PostgreSQL SQL file per operation
```

Services may not call other domain services directly. Cross-domain workflows
go through `backend/app/orchestration/`, whose mediator invokes typed ports.
The first implementation is in-process, but callers depend on ports rather
than concrete services. A later microservice extraction can replace a port
adapter with HTTP, RPC, or messaging without changing domain services.

`orchestration` is an application integration layer, not FastAPI HTTP
middleware. HTTP middleware remains reserved for request-wide concerns such as
logging or correlation IDs.

Runtime persistence continues to use readable SQL files under
`backend/app/queries/postgres/<domain>/`. SQLAlchemy models describe schema and
Alembic owns migrations; ORM query APIs are not used by repositories.

## Shared backend foundation

- Add `backend/app/orchestration/` with a small mediator and typed domain ports.
- Add authentication dependencies that resolve the JWT principal and enforce
  agent/admin roles.
- Add a consistent API error model and map domain errors at the HTTP boundary.
- Correct the Docker backend healthcheck to `/api/v1/health` and make required
  development environment values explicit in Compose.
- Configure the filesystem upload root as `/data/uploads` and mount a named
  Docker volume there.
- Update the project backend-development skill with the orchestration rule,
  folder ownership, and cross-domain examples.

## Authentication slice

Both agent and administrator sign-up are public in this version. Routes are
role-explicit so the same email may be registered independently for each role:

- `POST /api/v1/auth/agents/signup`
- `POST /api/v1/auth/agents/login`
- `POST /api/v1/auth/admins/signup`
- `POST /api/v1/auth/admins/login`
- `GET /api/v1/auth/me`

Passwords are never stored directly. The database stores an Argon2 password
hash. Agent registration captures a six-digit Indian pincode as a string so
leading zeroes are preserved. The pincode is geographic profile data, not an
authentication secret.

Login issues a signed, expiring bearer JWT containing the account ID and role.
Every protected request validates the signature and expiry, then verifies the
account still exists and is not soft-deleted. No token/session database or
refresh-token flow is added yet. Logout removes the client token.

The frontend provides separate agent/admin sign-up and login routes, persists
the bearer token for the current browser session, restores `/auth/me`, attaches
the token through one API client, and prevents cross-role navigation.

## Product catalogue slice

The normalized hierarchy is:

```text
ProductLineup 1 -> many Product 1 -> many ProductVariant
```

- A lineup has a generated ID, identifier/name, and optional description.
- A product has a generated ID, lineup ID, name, and optional description.
- A variant has a generated ID, product ID, optional display name, and `specs`.
- No SKU is required.

`specs` remains a simple text field in this draft. API contracts keep it behind
the variant resource boundary so a later JSON representation affects the
variant model, query files, and form only. Queries do not join unrelated domain
tables or embed product behavior in assignments/Q&A.

Administrators can create, list, view, update, and soft-delete lineups,
products, and variants. Agents have read-only catalogue access. Deleting a
parent with active children returns a conflict instead of silently cascading
business data.

## Assignment slice

Administrators create an assignment-generation request by selecting a product,
one or more agents, a deadline, a question count, and text mode. The application
orchestrator gathers product context through a product port and passes an
extensible `AssignmentGenerationContext` to the generator. The context contains
the current product/variant specifications plus an empty `additional_sources`
collection so future sources can be added without changing controllers.

The initial `MockAssignmentGenerator` deterministically creates questions from
product specifications. It is a placeholder, not an AI implementation. The
initial `MockAssignmentEvaluator` stores a clearly labeled placeholder
evaluation after an agent submits text answers. Both implement protocols and
are injected into the assignment orchestration flow.

Assignments store their product reference, creator, mode, deadline, lifecycle
status, and generated questions. Per-agent mappings and response rows keep each
agent's progress and answers separate. Agents can list assigned work, open an
assignment, save/submit answers once, and view the placeholder evaluation.
Administrators can list, inspect, update assignment metadata, and soft-delete
assignments.

The UI exposes both Text and Avatar modes. Text mode is functional. Avatar mode
is a disabled, accessible preview labeled “Coming later”; it does not simulate
speech or avatar behavior.

> **PENDING AI REPLACEMENT:** Replace `MockAssignmentGenerator` and
> `MockAssignmentEvaluator` with real adapters. Keep the orchestrator, ports,
> persistence contracts, and controller routes stable.

## Q&A slice

Agents select a product, submit a product question, and view their own paged
interaction history. Creating or editing an interaction calls a replaceable
answer-provider protocol through orchestration and stores both question and
response. Agents can view, update, and delete their own records; administrators
do not receive write access to agent conversations.

The initial provider returns a deterministic response that explicitly says it
is a placeholder and references only the selected product context. The history
UI must label responses as placeholder-generated.

> **PENDING AI REPLACEMENT:** Replace `MockProductAnswerProvider` with the real
> contextual answer service. The provider input already accepts
> `additional_sources` for future product-lineup material.

## Face attendance slice

An authenticated agent uploads exactly one JPEG, PNG, or WebP image per India
calendar day (`Asia/Kolkata`). A second upload for the same agent and date
returns HTTP 409 and does not replace the original.

`LocalFileStorage` writes to the configured Docker volume through a storage
protocol. The database stores agent ownership, attendance date, relative object
key, media metadata, analysis status, and a nullable text analysis result. File
paths are generated by the server and never accepted from clients. Upload size
and media type are validated before persistence.

The placeholder analyzer stores a clearly labeled string result and
`placeholder` status. Agents can upload and view their history. Administrators
can list attendance records and delete an erroneous record; deletion removes
both metadata and the local file through orchestration.

> **PENDING AI AND STORAGE REPLACEMENT:** Replace `MockFaceAnalyzer` with a real
> analyzer. Replace `LocalFileStorage` with object storage without changing the
> face service/controller contracts. The analysis-result repository boundary
> permits migration from text to JSON in a later schema draft.

## Frontend architecture and visual design

Replace the monolithic prototype with React Router feature routes, reusable
role-aware layouts, and feature folders. TanStack Query owns server state and
mutation invalidation. Redux is limited to authenticated-session state; the
starter counter is removed. One typed fetch client handles the API base URL,
Bearer header, JSON/multipart requests, and normalized errors.

Agent navigation contains Overview, Products, Q&A, Assignments, and Face
Attendance. Administrator navigation contains Overview, Products, Assignments,
and Attendance. All screens follow the repository brand skill: semantic purple
tokens, cool-gray background, white surfaces, restrained accent colors,
rounded cards and controls, visible focus states, and responsive navigation.

Forms show field-level/server errors, mutations expose pending/disabled states,
empty states explain the next action, and destructive actions require an
explicit confirmation. AI placeholders are identified by both text and status,
never color alone.

## Error and authorization behavior

- `400` for malformed domain input not covered by request validation.
- `401` for missing, invalid, or expired JWTs and incorrect credentials.
- `403` for a valid principal using a route outside its role.
- `404` for missing or soft-deleted resources.
- `409` for duplicate registration, parent deletion with children, already
  submitted assignments, or a second daily face photo.
- `413` for oversized photo uploads.
- `422` for Pydantic validation failures.

Database uniqueness constraints back application conflict checks. Services own
transactions; repositories neither create sessions nor commit independently.

## Testing and verification

Backend tests cover password hashing/JWT validation, role enforcement, CRUD
rules, orchestration ports, mock adapter labeling, one-photo-per-day behavior,
and migration structure. Integration tests exercise PostgreSQL through the
Docker stack and verify protected APIs with real tokens.

Frontend tests cover authentication restoration, route guards, catalogue CRUD
forms, assignment submission, Q&A history, face upload conflicts, avatar-stub
copy, and error/empty states. Lint and production build must pass.

Final verification runs:

```bash
docker compose config
docker compose up --build
cd backend && PYTHONPATH=. pytest -q
cd frontend && npm test -- --run
cd frontend && npm run lint
cd frontend && npm run build
```

The running application is then exercised in a browser at desktop and mobile
widths for both roles. The walkthrough covers sign-up/login, product CRUD,
assignment generation/submission, Q&A creation/history, face upload/history,
role denial, validation errors, and logout.

## Documentation

Maintain service documentation under `backend/app/docs/` for authentication,
orchestration, products, assignments, Q&A, and face attendance. Each multi-step
flow includes a Mermaid sequence diagram. Diagram participants for mock AI
adapters are labeled `PENDING AI REPLACEMENT`; implemented components are
labeled `IMPLEMENTED`. The README documents setup, environment variables,
volume behavior, test commands, route entry points, and deferred integrations.

## Out of scope

- Real AI generation, evaluation, Q&A, or face analysis.
- Avatar speech, animation, recording, or speech recognition.
- Email confirmation, password reset, refresh tokens, or third-party login.
- External object storage.
- Distributed message brokers or actual microservice deployment.
- JSON face-analysis payloads; the later draft will finalize that schema.
