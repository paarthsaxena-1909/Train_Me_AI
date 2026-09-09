SELECT a._id AS id, a.product_lineup_id, l.lineup_identifier, a.status,
       q._id AS question_id, q.question_number, q.question, q.answer, q.evaluation
FROM assignments a JOIN product_lineups l ON l._id = a.product_lineup_id
JOIN assignment_agent_mapping m ON m.assignment_id = a._id
LEFT JOIN assignment_questions q ON q.assignment_id = a._id AND q."deletedAt" IS NULL
WHERE a._id = :assignment_id AND m.agent_id = :agent_id AND a."deletedAt" IS NULL;
