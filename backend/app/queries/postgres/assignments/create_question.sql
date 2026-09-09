INSERT INTO assignment_questions (assignment_id, question_number, question) VALUES (:assignment_id, :question_number, :question)
RETURNING _id AS id, question_number, question, answer, evaluation;
