UPDATE assignments SET status = 'completed', "updatedAt" = now()
WHERE _id = :assignment_id AND "deletedAt" IS NULL;
