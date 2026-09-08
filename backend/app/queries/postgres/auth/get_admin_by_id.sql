SELECT
    _id AS id,
    email,
    password_hash,
    name,
    NULL AS region,
    NULL AS pincode,
    'admin' AS role,
    "deletedAt" AS deleted_at
FROM admins
WHERE _id = :account_id
  AND "deletedAt" IS NULL;
