# Authentication

Authentication is role-explicit: agents and administrators each have public
signup and login routes, while protected workspace routes restore the current
account through `GET /api/v1/auth/me`.

## Routes

- `/agent/signup` and `/agent/login`
- `/admin/signup` and `/admin/login`
- `/api/v1/auth/agents/{signup,login}`
- `/api/v1/auth/admins/{signup,login}`
- `/api/v1/auth/me`

The access token is kept in `sessionStorage` under the versioned
`train-me-auth-token-v1` key. It is attached as a bearer token by the shared API
client, and is removed when session restoration receives a 401 or when the
user logs out. Account identity remains in Redux memory and is refreshed from
the backend on a new page load.

Agent signup requires a six-digit pincode and preserves leading zeroes. Admin
signup intentionally has no pincode field. The server response determines the
redirect role, so a mismatched role can never open the other workspace.
