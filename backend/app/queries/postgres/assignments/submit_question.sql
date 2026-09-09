UPDATE assignment_questions SET answer = :answer, evaluation = :evaluation, "updatedAt" = now()
WHERE _id = :question_id AND assignment_id = :assignment_id AND "deletedAt" IS NULL;
