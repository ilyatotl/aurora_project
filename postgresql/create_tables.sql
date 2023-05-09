CREATE TABLE applications
(
    id                BIGSERIAL PRIMARY KEY,
    name              TEXT NOT NULL,
    developer         TEXT NOT NULL,
    version           TEXT NOT NULL,
    short_description TEXT NOT NULL,
    long_description  TEXT NOT NULL
);

CREATE TABLE users
(
    id                 BIGSERIAL PRIMARY KEY,
    full_name          TEXT NOT NULL,
    username           TEXT NOT NULL,
    email              TEXT NOT NULL,
    encrypted_password TEXT NOT NULL
);