# Authentication service

Authentication owns public signup/login for agents and admins and protected account lookup. Agent signup requires a six-digit Indian pincode; admin signup is public for now. Passwords are Argon2-hashed and JWTs contain account ID, role, issued-at, and expiry claims. The request dependency decodes the token and re-reads the active account from the role table. There is no token/session table or refresh-token rotation yet.

Routes: `POST /api/v1/auth/agents/signup`, `POST /api/v1/auth/admins/signup`, role-specific login routes, and `GET /api/v1/auth/me`. Controllers depend on `AuthService`; persistence is isolated in `AuthRepository` and SQL. Future refresh-token storage and revocation can be added behind the token boundary.

Flows: [signup](flows/signup.md), [login](flows/login.md), [authenticate request](flows/authenticate-request.md).
