SET search_path TO sales_portfolio;

CREATE OR REPLACE VIEW dim_customers AS
SELECT
    customer_key,
    first_name,
    last_name,
    CONCAT_WS(' ', first_name, last_name) AS full_name,
    CASE
        WHEN gender = 'M' THEN 'Male'
        WHEN gender = 'F' THEN 'Female'
        ELSE 'Unknown'
    END AS gender,
    date_first_purchase,
    EXTRACT(YEAR FROM date_first_purchase)::INTEGER AS first_purchase_year,
    COALESCE(NULLIF(TRIM(customer_city), ''), 'Not Registered') AS customer_city
FROM raw_customers;
