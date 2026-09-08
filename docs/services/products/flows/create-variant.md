# Create variant (IMPLEMENTED)

```mermaid
sequenceDiagram
 participant Admin
 participant API as Products controller
 participant Auth as CurrentAdmin
 participant Service as ProductsService
 participant Repo as ProductsRepository
 participant DB as PostgreSQL
 Admin->>API: POST /products/{id}/variants + JWT
 API->>Auth: authorize admin
 Auth-->>API: principal (IMPLEMENTED)
 API->>Service: typed VariantCreate
 Service->>Repo: product_exists(product_id)
 Repo->>DB: SELECT active product by ID
 DB-->>Repo: product exists or missing
 alt Product exists
 Service->>Repo: create variant
 Repo->>DB: Resolve product.product_lineup_id
 Repo->>DB: INSERT variant(product_lineup_id, name, specs)
  Repo->>DB: INSERT new product(lineup_id, variant_id)
  DB-->>Service: generated ID and fields
  Service-->>API: VariantResponse
  API-->>Admin: 201 Created
 else Product missing or deleted
  Service-->>API: raise NotFoundError
  API-->>Admin: 404 Product not found
 end
```

The service verifies that the referenced product exists and is not soft-deleted
before inserting the variant. PostgreSQL additionally enforces the
`product_variants.product_lineup_id` foreign key. A variant belongs to a lineup;
the concrete `products` row links that lineup and variant. A new variant creates
a new product-combination row; it never overwrites the existing product.
Variants have no SKU. Editing and deletion are deferred.
