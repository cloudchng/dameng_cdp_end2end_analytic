-- ==========================================
-- CLOUDERA ICEBERG TABLES SETUP (IMPALA/HUE)
-- ==========================================

CREATE DATABASE IF NOT EXISTS dameng;

-- 1. TRANSACTIONS
CREATE TABLE dameng.transactions (
    tx_id BIGINT,
    user_id INT,
    merchant_id INT,
    amount DOUBLE,
    tx_time TIMESTAMP,
    status STRING,
    city STRING 
) STORED AS ICEBERG;

-- 2. CUSTOMERS
CREATE TABLE dameng.customers (
    customer_id INT,
    name STRING,
    age INT,
    credit_limit DOUBLE,
    risk_profile STRING,
    created_at TIMESTAMP
) STORED AS ICEBERG;

-- 3. MERCHANTS
CREATE TABLE dameng.merchants (
    merchant_id INT,
    merchant_name STRING,
    category STRING,
    risk_level STRING,
    city STRING,
    created_at TIMESTAMP
) STORED AS ICEBERG;

-- 4. ACCOUNTS
CREATE TABLE dameng.accounts (
    account_id STRING,
    customer_id INT,
    account_type STRING,
    balance DOUBLE,
    currency STRING,
    status STRING,
    opened_at TIMESTAMP
) STORED AS ICEBERG;
