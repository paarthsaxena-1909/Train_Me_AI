# Application orchestration

`backend/app/orchestration/` is the typed application integration boundary for
cross-domain workflows. It is an in-process mediator/port layer, not FastAPI
HTTP middleware. Domain services must not import or call another domain
service directly, duplicate its persistence logic, or read its tables from
their own repository. When a service needs information it does not own, it
asks the owning domain through a mediator-registered port.
The concrete port adapter delegates to an existing owning-domain service flow;
it does not add business rules or bypass that flow with direct database calls.

## Allowed flow

Controllers call their own service, and a service may request another domain
through a `DomainPort` registered with `ServiceMediator`:

```python
class ProductContextPort(DomainPort[ProductContextRequest, ProductContext]):
    ...

mediator.register("products.context", product_context_port)
context = await mediator.request("products.context", request)
```

## Forbidden flow

```python
# Do not import concrete domain services into another service.
from app.services.product_service import ProductService

context = await ProductService(...).get_context(product_id)
```

Keep ports generic and free of concrete service imports. HTTP middleware is
reserved for request-wide concerns such as CORS, logging, and correlation IDs.
The mediator is intentionally small so a future adapter can replace an
in-process handler with HTTP, RPC, or messaging without changing callers.
