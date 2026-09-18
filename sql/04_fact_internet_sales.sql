SET search_path TO sales_portfolio;

-- Joining to the calendar makes invalid date keys visible instead of treating them
-- as valid text. Two source rows use 20190229 and are excluded from this view.
CREATE OR REPLACE VIEW fact_internet_sales AS
SELECT
    sales.product_key,
    sales.order_date_key,
    sales.due_date_key,
    sales.ship_date_key,
    sales.customer_key,
    sales.sales_order_number,
    sales.sales_amount
FROM raw_internet_sales AS sales
INNER JOIN raw_calendar AS calendar
    ON calendar.date_key = sales.order_date_key
WHERE calendar.full_date_alternate_key >= DATE '2019-01-01';
