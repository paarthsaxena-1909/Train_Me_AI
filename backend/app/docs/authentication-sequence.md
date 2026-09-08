# Authentication flow

Authentication is role-explicit because agents and administrators live in
separate tables. Both signup routes are public. Signup normalizes the email,
validates an agent pincode as a six-digit string, hashes the password with
Argon2 through `pwdlib`, and commits the row through `AuthService`.

Each role has its own login route. The service reads only that role's active
row, verifies the submitted password against `password_hash`, and issues a
signed JWT containing `sub`, `role`, `iat`, and `exp`. `TokenService` decodes
with the configured algorithm only; malformed, expired, or differently
algorithmed tokens return HTTP 401.

`CurrentPrincipal` validates the bearer token and re-reads the account from
the matching table with `deletedAt IS NULL`. `CurrentAgent` and
`CurrentAdmin` then enforce role-specific access and return HTTP 403 when the
principal has the other role. There is intentionally no token/session table,
refresh token, or server-side revocation flow yet. A future refresh-token
store can support rotation and revocation, while a session/version field can
invalidate access tokens before their expiry.

## IMPLEMENTED sequence

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant Service as AuthService
    participant Passwords as Argon2/pwdlib
    participant Repo as AuthRepository
    participant DB as PostgreSQL
    participant Tokens as TokenService

    Client->>Controller: POST role signup
    Controller->>Service: validated signup payload
    Service->>Passwords: hash(password)
    Service->>Repo: create role row(password_hash, profile)
    Repo->>DB: role-specific INSERT SQL
    DB-->>Repo: account row
    Service->>DB: commit
    Controller-->>Client: 201 account

    Client->>Controller: POST role login
    Controller->>Service: validated credentials
    Service->>Repo: get role by normalized email
    Repo->>DB: role-specific SELECT SQL
    DB-->>Repo: active account row
    Service->>Passwords: verify(password, password_hash)
    Service->>Tokens: create(sub, role, iat, exp)
    Tokens-->>Client: signed bearer JWT

    Client->>Controller: GET /auth/me + bearer JWT
    Controller->>Tokens: decode configured algorithm
    Tokens-->>Controller: Principal(account_id, role)
    Controller->>Repo: re-check active account by id
    Repo->>DB: role-specific active SELECT SQL
    DB-->>Controller: current account or no row
    Controller-->>Client: account or 401/403
```
