INSERT INTO product_variants (name, specs, product_lineup_id) VALUES (:name, :specs, :product_lineup_id) RETURNING _id AS id, name, specs;
