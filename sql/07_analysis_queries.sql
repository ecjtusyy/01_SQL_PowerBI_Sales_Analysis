SET search_path TO sales_portfolio;

-- Monthly sales and budget. Restrict portfolio conclusions to complete periods.
WITH monthly_sales AS (
    SELECT
        calendar.month_start,
        SUM(sales.sales_amount) AS sales_amount,
        COUNT(DISTINCT sales.sales_order_number) AS order_count
    FROM fact_internet_sales AS sales
    INNER JOIN dim_calendar AS calendar
        ON calendar.date_key = sales.order_date_key
    GROUP BY calendar.month_start
)
SELECT
    sales.month_start,
    sales.sales_amount,
    budget.budget_amount,
    sales.sales_amount - budget.budget_amount AS budget_variance,
    sales.sales_amount / NULLIF(budget.budget_amount, 0) AS budget_attainment,
    sales.order_count
FROM monthly_sales AS sales
LEFT JOIN fact_budget AS budget
    ON budget.budget_month = sales.month_start
ORDER BY sales.month_start;

-- Product-category contribution.
SELECT
    product.product_category,
    SUM(sales.sales_amount) AS sales_amount,
    SUM(sales.sales_amount)
        / NULLIF(SUM(SUM(sales.sales_amount)) OVER (), 0) AS sales_share
FROM fact_internet_sales AS sales
INNER JOIN dim_products AS product
    ON product.product_key = sales.product_key
GROUP BY product.product_category
ORDER BY sales_amount DESC;

-- Top products by sales.
SELECT
    product.product_name,
    SUM(sales.sales_amount) AS sales_amount,
    COUNT(DISTINCT sales.sales_order_number) AS order_count
FROM fact_internet_sales AS sales
INNER JOIN dim_products AS product
    ON product.product_key = sales.product_key
GROUP BY product.product_name
ORDER BY sales_amount DESC
LIMIT 10;
