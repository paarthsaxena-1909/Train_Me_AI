INSERT INTO agents (email, password_hash, name, region, pincode)
VALUES (LOWER(:email), :password_hash, :name, :region, :pincode)
RETURNING
    _id AS id,
    email,
    password_hash,
    name,
    region,
    pincode,
    'agent' AS role,
    "deletedAt" AS deleted_at;
