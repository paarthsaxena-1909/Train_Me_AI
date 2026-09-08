INSERT INTO agent_queries (query, response, product_id)
VALUES (:query, :response, :product_id)
RETURNING _id AS id, query, response, product_id;
