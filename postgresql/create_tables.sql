CREATE TABLE applications
(
    id                BIGSERIAL PRIMARY KEY,
    name              TEXT NOT NULL,
    developer         TEXT NOT NULL,
    version           TEXT NOT NULL,
    short_description TEXT NOT NULL,
    long_description  TEXT NOT NULL
);