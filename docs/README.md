# Train Me AI documentation

Service documentation is organized by ownership. Each service README describes its boundaries, routes, data, and extension points. Multi-step workflows live in that service's `flows/` directory, with one Mermaid sequence diagram per flow.

## Services

- [Authentication](services/authentication/README.md): [signup](services/authentication/flows/signup.md), [login](services/authentication/flows/login.md), [request authentication and role authorization](services/authentication/flows/authenticate-request.md)
- [Logging](services/logging/README.md): [configure and emit](services/logging/flows/configure-and-emit.md)
- [Orchestration](services/orchestration/README.md): [mediated request](services/orchestration/flows/mediated-request.md)
- [Health](services/health/README.md): [health check](services/health/flows/health-check.md)
- [Products](services/products/README.md): [create product](services/products/flows/create-product.md), [create variant](services/products/flows/create-variant.md), [list catalogue](services/products/flows/list-catalogue.md)
- [Q&A](services/qa/README.md): [ask one product question](services/qa/flows/ask-question.md)

AI response generation, avatar delivery, face analysis, and object storage remain deferred and must be marked clearly when documented.
