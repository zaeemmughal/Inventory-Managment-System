-- =============================================================
--  Inventory Management System - Full Schema
--  Run once against a MySQL server:
--    mysql -u root -p < schema.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS inventory;
USE inventory;

-- ---- users (login accounts, hashed passwords) ----
CREATE TABLE IF NOT EXISTS users (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    username            VARCHAR(50)  UNIQUE NOT NULL,
    password            VARCHAR(255) NOT NULL,
    salt                VARCHAR(64)  NOT NULL,
    securityQuestion    VARCHAR(255) NOT NULL,
    securityAnswer      VARCHAR(255) NOT NULL,
    securityAnswerSalt  VARCHAR(64)  NOT NULL
);

-- ---- employees ----
CREATE TABLE IF NOT EXISTS employees (
    empid       INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100),
    gender      VARCHAR(10),
    dob         DATE,
    email       VARCHAR(100),
    contact     VARCHAR(15),
    address     TEXT,
    education   VARCHAR(50),
    doj         DATE,
    jobType     VARCHAR(50),
    workShift   VARCHAR(50),
    salary      FLOAT,
    userType    VARCHAR(50),
    password    VARCHAR(50)
);

-- ---- suppliers ----
CREATE TABLE IF NOT EXISTS suppliers (
    invoice     INT PRIMARY KEY,
    name        VARCHAR(100),
    contact     VARCHAR(50),
    description TEXT
);

-- ---- categories ----
CREATE TABLE IF NOT EXISTS categories (
    id          INT PRIMARY KEY,
    name        VARCHAR(100),
    description TEXT
);

-- ---- products ----
CREATE TABLE IF NOT EXISTS products (
    id              INT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    price           FLOAT        NOT NULL,
    quantity        INT          NOT NULL,
    category_id     INT          NOT NULL,
    supplier_id     INT          NOT NULL,
    status          VARCHAR(20),
    payment_method  VARCHAR(30),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(invoice)
);

-- ---- sales ----
CREATE TABLE IF NOT EXISTS sales (
    sale_id         INT AUTO_INCREMENT PRIMARY KEY,
    product_id      INT   NOT NULL,
    quantity        INT   NOT NULL,
    total           FLOAT NOT NULL,
    payment_method  VARCHAR(30),
    sale_date       DATE  NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
