# Orchestration boundary

`ServiceMediator` dispatches typed ports between domains. Domain services do not import or call one another directly. The in-process adapter can later be replaced by HTTP, RPC, or messaging without changing callers. This is an application boundary, not HTTP middleware.

Flow: [mediated request](flows/mediated-request.md).

## How it works today

The current application is a modular monolith. A consuming workflow requests a
stable route from `ServiceMediator`, which invokes a registered in-process
adapter. For product context, the adapter implements `ProductContextPort` and
uses `ProductsRepository`; it does not call `ProductsService` directly.

```text
Assignment or Q&A flow
        ↓
ServiceMediator: product.get_context
        ↓
RepositoryProductContext
        ↓
ProductsRepository → product SQL → PostgreSQL
```

The port is the contract and the adapter is the replaceable implementation.
This keeps consuming services independent of product-service internals.

## Microservice migration

When product management moves to its own service, the consuming workflow and
port contract can stay stable. Replace the in-process adapter with an
`HttpProductContextAdapter` or RPC adapter, then register that adapter under the
same mediator route:

```text
Assignment service
        ↓
ServiceMediator: product.get_context
        ↓
HTTP/RPC ProductContextAdapter
        ↓
Product service API → Product service database
```

Only the composition/wiring layer changes. The migration boundary also gives us
one place to add internal service authentication, timeouts, retries, circuit
breakers, contract versioning, tracing, and unavailable-service handling.
The mediator is therefore an application routing boundary—not HTTP middleware
and not a second business-logic layer.
