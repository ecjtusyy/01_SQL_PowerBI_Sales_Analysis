SET search_path TO sales_portfolio;

-- Invalid order date keys. The supplied source returns 20190229 with 2 rows.
SELECT
    sales.order_date_key,
    COUNT(*) AS affected_rows,
    SUM(sales.sales_amount) AS affected_sales_amount
FROM raw_internet_sales AS sales
LEFT JOIN raw_calendar AS calendar
    ON calendar.date_key = sales.order_date_key
WHERE calendar.date_key IS NULL
GROUP BY sales.order_date_key
ORDER BY affected_rows DESC;

-- Foreign-key coverage checks for customer and product dimensions.
SELECT
    COUNT(*) FILTER (WHERE customer.customer_key IS NULL) AS unmatched_customer_rows,
    COUNT(*) FILTER (WHERE product.product_key IS NULL) AS unmatched_product_rows
FROM fact_internet_sales AS sales
LEFT JOIN dim_customers AS customer
    ON customer.customer_key = sales.customer_key
LEFT JOIN dim_products AS product
    ON product.product_key = sales.product_key;

-- Budget months after the final available sale should not be compared as zero sales.
SELECT
    MIN(calendar.calendar_date) AS first_sale_date,
    MAX(calendar.calendar_date) AS last_sale_date,
    MAX(budget.budget_month) AS last_budget_month
FROM fact_internet_sales AS sales
INNER JOIN dim_calendar AS calendar
    ON calendar.date_key = sales.order_date_key
CROSS JOIN fact_budget AS budget;
