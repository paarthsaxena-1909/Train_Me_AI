# Cross-domain orchestration

The mediator is an application integration boundary. It dispatches typed
ports in-process today and leaves room for a transport adapter later.

```mermaid
sequenceDiagram
    participant C as Controller (IMPLEMENTED)
    participant S as Calling service (IMPLEMENTED)
    participant M as ServiceMediator (IMPLEMENTED)
    participant P as DomainPort (IMPLEMENTED)
    participant D as Target domain adapter (IMPLEMENTED)

    C->>S: request
    S->>M: request(route, payload)
    M->>P: dispatch(payload)
    P->>D: invoke typed operation
    D-->>P: typed result
    P-->>M: typed result
    M-->>S: result
    S-->>C: response
```

Concrete service-to-service imports are forbidden. A future remote adapter is
`PENDING AI REPLACEMENT` only in the transport sense: the port contract stays
implemented while the in-process adapter may be replaced by HTTP, RPC, or
messaging.
