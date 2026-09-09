INSERT INTO assignments (product_lineup_id, status) VALUES (:product_lineup_id, NULL)
RETURNING _id AS id, product_lineup_id, status;
