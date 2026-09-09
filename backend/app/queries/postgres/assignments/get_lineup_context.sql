SELECT l._id AS id, l.lineup_identifier, p.name AS product_name, p.description,
       v.name AS variant_name, v.specs
FROM product_lineups l
LEFT JOIN products p ON p.product_lineup_id = l._id AND p."deletedAt" IS NULL
LEFT JOIN product_variants v ON v.product_lineup_id = l._id AND v."deletedAt" IS NULL
WHERE l._id = :product_lineup_id AND l."deletedAt" IS NULL
ORDER BY p._id, v._id;
