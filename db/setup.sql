CREATE DATABASE example;
\c example
CREATE TABLE users(
    email VARCHAR(255) PRIMARY KEY,
    hash VARCHAR(255) NOT NULL
);
