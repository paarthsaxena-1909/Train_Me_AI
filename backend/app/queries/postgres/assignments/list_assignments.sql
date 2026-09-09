SELECT a._id AS id, a.product_lineup_id, l.lineup_identifier, a.status
FROM assignments a JOIN product_lineups l ON l._id = a.product_lineup_id
JOIN assignment_agent_mapping m ON m.assignment_id = a._id
WHERE m.agent_id = :agent_id AND a."deletedAt" IS NULL AND l."deletedAt" IS NULL
  AND (CAST(:product_lineup_id AS INTEGER) IS NULL OR a.product_lineup_id = CAST(:product_lineup_id AS INTEGER))
ORDER BY a._id DESC;
