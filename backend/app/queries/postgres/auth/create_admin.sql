INSERT INTO admins (email, password_hash, name)
VALUES (LOWER(:email), :password_hash, :name)
RETURNING
    _id AS id,
    email,
    password_hash,
    name,
    NULL AS region,
    NULL AS pincode,
    'admin' AS role,
    "deletedAt" AS deleted_at;
