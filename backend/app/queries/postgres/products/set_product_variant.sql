INSERT INTO products (name, description, product_lineup_id, product_variant_id)
SELECT name, description, product_lineup_id, :variant_id
FROM products
WHERE _id = :product_id AND "deletedAt" IS NULL
RETURNING _id AS id, name, description, product_lineup_id, product_variant_id;
