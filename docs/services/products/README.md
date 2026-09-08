# Product catalogue service

The catalogue models a product as a concrete product-lineup plus variant
combination. A `ProductLineup` must always have at least one variant. Product
creation atomically creates the lineup, its first `ProductVariant`, and the
`Product` combination row. Additional variants belong to the same lineup and
create additional product-combination rows. There is no SKU, editing, or
deletion in this scope.

Write routes require `CurrentAdmin`; read routes require an authenticated principal. The controller → service → repository → SQL boundary stays modular. `ProductContextPort` exposes product/variant context for future assignments and Q&A without direct service-to-service calls.

Before creating a variant, `ProductsService` uses `product_exists.sql` to
confirm that its parent product exists and is active. A missing or soft-deleted
product produces HTTP 404 without attempting the insert. The database foreign
key provides an additional integrity check. Variant creation never updates the
existing product's variant; it inserts a new concrete `Product` row instead.

Flows: [create product](flows/create-product.md), [create variant](flows/create-variant.md), [list catalogue](flows/list-catalogue.md).
