# Application orchestration

`backend/app/orchestration/` is the typed application integration boundary for
cross-domain workflows. It is an in-process mediator/port layer, not FastAPI
HTTP middleware. Domain services must not import or call another domain
service directly.

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
