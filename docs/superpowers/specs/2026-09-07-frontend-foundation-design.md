# Frontend Foundation Design

## Goal

Create a minimal, runnable frontend foundation in `frontend/` using React, TypeScript, Redux Toolkit, TanStack Query, and Tailwind CSS.

## Architecture

The frontend will be a Vite-powered React application. `main.tsx` will compose the Redux `<Provider>` and TanStack Query `<QueryClientProvider>` around the root app, while Tailwind will provide utility styling through the global stylesheet. A small Redux slice and a query-backed starter component will prove both state-management paths are wired without introducing backend-specific assumptions.

## Scope

- Create the application under `frontend/`.
- Use TypeScript throughout application source and configuration where supported.
- Configure Tailwind CSS with PostCSS and content scanning for `src`.
- Add Redux Toolkit and React Redux with a starter counter slice.
- Add TanStack Query with a local, deterministic example query.
- Provide npm scripts for development, build, preview, and lint.
- Keep routing, authentication, API clients, and backend integration out of scope.

## Success criteria

- `npm install` completes in `frontend/`.
- `npm run build` completes successfully.
- The starter page renders Tailwind styles and demonstrates Redux and TanStack Query wiring.
- No generated dependency directories are committed.
