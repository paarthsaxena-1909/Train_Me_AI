SELECT lineup._id AS id, lineup.lineup_identifier, COUNT(DISTINCT product._id)::int AS product_count
FROM product_lineups AS lineup
LEFT JOIN products AS product ON product.product_lineup_id = lineup._id AND product."deletedAt" IS NULL
WHERE lineup."deletedAt" IS NULL
GROUP BY lineup._id, lineup.lineup_identifier
ORDER BY lineup._id;
