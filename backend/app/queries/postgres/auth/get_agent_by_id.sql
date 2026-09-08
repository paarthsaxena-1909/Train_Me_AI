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
WHERE _id = :account_id
  AND "deletedAt" IS NULL;
