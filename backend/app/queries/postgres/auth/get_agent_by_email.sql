SELECT
    _id AS id,
    email,
    password_hash,
    name,
    region,
    pincode,
    'agent' AS role,
    "deletedAt" AS deleted_at
FROM agents
WHERE LOWER(email) = LOWER(:email)
  AND "deletedAt" IS NULL;
