SELECT 1 AS exists FROM products WHERE _id = :product_id AND "deletedAt" IS NULL;
