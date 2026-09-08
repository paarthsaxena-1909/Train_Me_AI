SELECT variant._id AS id, variant.name, variant.specs
FROM product_variants AS variant
JOIN products AS product ON product.product_lineup_id = variant.product_lineup_id
WHERE product._id = :product_id AND variant."deletedAt" IS NULL
ORDER BY variant._id;
