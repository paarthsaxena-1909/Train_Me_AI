SELECT product_lineup_id FROM products
WHERE _id = :product_id AND "deletedAt" IS NULL;
