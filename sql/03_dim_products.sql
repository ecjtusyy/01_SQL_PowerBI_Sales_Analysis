SET search_path TO sales_portfolio;

CREATE OR REPLACE VIEW dim_products AS
SELECT
    product_key,
    product_item_code,
    product_name,
    COALESCE(NULLIF(TRIM(sub_category), ''), 'Not Registered') AS sub_category,
    COALESCE(NULLIF(TRIM(product_category), ''), 'Not Registered') AS product_category,
    COALESCE(NULLIF(NULLIF(TRIM(product_color), ''), 'NA'), 'Not Registered') AS product_color,
    COALESCE(NULLIF(TRIM(product_size), ''), 'Not Registered') AS product_size,
    COALESCE(NULLIF(TRIM(product_line), ''), 'Not Registered') AS product_line,
    COALESCE(NULLIF(TRIM(product_model_name), ''), 'Not Registered') AS product_model_name,
    COALESCE(NULLIF(TRIM(product_description), ''), 'Not Registered') AS product_description,
    COALESCE(NULLIF(TRIM(product_status), ''), 'Not Registered') AS product_status
FROM raw_products;
