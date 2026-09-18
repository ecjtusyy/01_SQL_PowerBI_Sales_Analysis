SET search_path TO sales_portfolio;

CREATE OR REPLACE VIEW dim_calendar AS
SELECT
    date_key,
    full_date_alternate_key AS calendar_date,
    EXTRACT(YEAR FROM full_date_alternate_key)::INTEGER AS calendar_year,
    EXTRACT(QUARTER FROM full_date_alternate_key)::INTEGER AS calendar_quarter,
    month_number_of_year AS month_number,
    month_name,
    LEFT(month_name, 3) AS month_short_name,
    day_name,
    EXTRACT(DAY FROM full_date_alternate_key)::INTEGER AS day_of_month,
    DATE_TRUNC('month', full_date_alternate_key)::DATE AS month_start
FROM raw_calendar
WHERE full_date_alternate_key >= DATE '2019-01-01';
