INSERT INTO product_lineups (lineup_identifier) VALUES (:lineup_identifier)
RETURNING _id AS id;
