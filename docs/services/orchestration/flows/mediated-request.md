# Mediated cross-domain request (IMPLEMENTED)

```mermaid
sequenceDiagram
 participant C as Controller
 participant S as Calling service
 participant M as ServiceMediator
 participant P as Typed port
 participant D as Target adapter
 C->>S: request
 S->>M: request(route, payload)
 M->>P: dispatch typed payload
 P->>D: invoke operation
 D-->>M: typed result
 M-->>S: result
 S-->>C: response (IMPLEMENTED)
```

Today, `D` is an in-process adapter such as `RepositoryProductContext`.
During a microservice migration, `D` can be replaced by an HTTP, RPC, or
message adapter while the mediator route and consuming service contract remain
unchanged. Network concerns belong in that adapter, including service
authentication, timeouts, retries, version checks, and tracing.
