SET search_path TO sales_portfolio;

CREATE OR REPLACE VIEW fact_budget AS
SELECT
    budget_month,
    budget_amount
FROM raw_sales_budget;
