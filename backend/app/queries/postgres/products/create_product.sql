WITH lineup AS (
    INSERT INTO product_lineups (lineup_identifier) VALUES (:name)
    RETURNING _id
), variant AS (
    INSERT INTO product_variants (name, specs, product_lineup_id)
    SELECT :variant_name, :variant_specs, _id FROM lineup
    RETURNING _id, product_lineup_id
)
INSERT INTO products (name, description, product_lineup_id, product_variant_id)
SELECT :name, :description, product_lineup_id, _id FROM variant
RETURNING _id AS id, name, description, product_lineup_id, product_variant_id;
