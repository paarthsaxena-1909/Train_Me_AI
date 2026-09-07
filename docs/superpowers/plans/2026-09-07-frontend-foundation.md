# Frontend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a minimal Vite React TypeScript frontend with Tailwind CSS, Redux Toolkit, and TanStack Query wired and buildable.

**Architecture:** A Vite entrypoint mounts the React tree. Redux Toolkit owns a small local counter slice, while TanStack Query is configured at the app boundary and serves a deterministic starter query. Tailwind is loaded through the global CSS entrypoint and scans the source tree.

**Tech Stack:** Vite, React, TypeScript, Redux Toolkit, React Redux, TanStack Query, Tailwind CSS, PostCSS, ESLint.

**Spec:** `docs/superpowers/specs/2026-09-07-frontend-foundation-design.md`

## Global Constraints

- Application code lives under `frontend/`.
- Use TypeScript for application source.
- Keep routing, authentication, API clients, and backend integration out of scope.
- Verify the production build with `npm run build`.

---

### Task 1: Scaffold the frontend package

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/eslint.config.js`
- Create: `frontend/.gitignore`

**Interfaces:**
- Produces npm scripts `dev`, `build`, `lint`, and `preview` plus the dependency graph required by later tasks.

- [ ] **Step 1: Create the package manifest and Vite/TypeScript configuration**

Use React 19-compatible Vite dependencies, TypeScript, ESLint, Tailwind/PostCSS, Redux Toolkit, React Redux, and TanStack Query. Configure `build` as `tsc -b && vite build` and `lint` as `eslint .`.

- [ ] **Step 2: Install dependencies**

Run: `cd frontend && npm install`

Expected: npm creates `package-lock.json` and installs dependencies without committing `node_modules`.

- [ ] **Step 3: Verify the scaffold**

Run: `cd frontend && npm run lint`

Expected: ESLint exits with code 0 once the source files from Task 2 exist.

### Task 2: Wire providers and starter state/query behavior

**Files:**
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/app/store.ts`
- Create: `frontend/src/features/counter/counterSlice.ts`
- Create: `frontend/src/index.css`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tailwind.config.ts`

**Interfaces:**
- Produces a Redux store exported from `src/app/store.ts`.
- Produces a `counter` slice with `increment` and `decrement` actions.
- Produces a root app wrapped in Redux and TanStack Query providers.

- [ ] **Step 1: Configure Tailwind and PostCSS**

Add Tailwind directives to `src/index.css`; configure content scanning for `./src/**/*.{js,ts,jsx,tsx}`.

- [ ] **Step 2: Define the Redux slice and store**

Create a typed counter slice with initial state `{ value: 0 }`, then configure the store with that reducer and export `RootState` and `AppDispatch` types.

- [ ] **Step 3: Implement the starter app**

Create a page that displays the Redux counter with increment/decrement buttons and a TanStack Query result from a deterministic local promise. Use Tailwind classes to make the integration visible.

- [ ] **Step 4: Mount providers**

Create one `QueryClient`, wrap the app with `QueryClientProvider` and Redux `Provider`, and import the Tailwind stylesheet from `main.tsx`.

### Task 3: Verify the complete frontend

**Files:**
- Modify: `frontend/.gitignore` if needed after install.

- [ ] **Step 1: Run lint**

Run: `cd frontend && npm run lint`

Expected: exit code 0 with no lint errors.

- [ ] **Step 2: Run the production build**

Run: `cd frontend && npm run build`

Expected: TypeScript compilation and Vite bundling complete successfully.

- [ ] **Step 3: Inspect the final file set**

Run: `git status --short`

Expected: only the frontend source/configuration plus the approved spec and plan are untracked or modified; `node_modules` and build output are ignored.
