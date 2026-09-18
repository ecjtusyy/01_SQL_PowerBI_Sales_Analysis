-- PostgreSQL source contract for the portfolio project.
-- Load the files in data/raw into these tables before running the views below.

CREATE SCHEMA IF NOT EXISTS sales_portfolio;
SET search_path TO sales_portfolio;

CREATE TABLE IF NOT EXISTS raw_calendar (
    date_key INTEGER PRIMARY KEY,
    full_date_alternate_key DATE NOT NULL,
    day_name TEXT NOT NULL,
    month_name TEXT NOT NULL,
    month_number_of_year SMALLINT NOT NULL,
    calendar_quarter SMALLINT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_customers (
    customer_key INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    gender TEXT,
    date_first_purchase DATE NOT NULL,
    customer_city TEXT
);

CREATE TABLE IF NOT EXISTS raw_products (
    product_key INTEGER PRIMARY KEY,
    product_item_code TEXT,
    product_name TEXT NOT NULL,
    sub_category TEXT,
    product_category TEXT,
    product_color TEXT,
    product_size TEXT,
    product_line TEXT,
    product_model_name TEXT,
    product_description TEXT,
    product_status TEXT
);

CREATE TABLE IF NOT EXISTS raw_internet_sales (
    product_key INTEGER NOT NULL,
    order_date_key INTEGER NOT NULL,
    due_date_key INTEGER,
    ship_date_key INTEGER,
    customer_key INTEGER NOT NULL,
    sales_order_number TEXT NOT NULL,
    sales_amount NUMERIC(18, 4) NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_sales_budget (
    budget_month DATE PRIMARY KEY,
    budget_amount NUMERIC(18, 2) NOT NULL
);
