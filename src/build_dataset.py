"""Build clean Power BI input tables and verified KPI summaries.

Run from the repository root:
    python src/build_dataset.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
START_DATE = pd.Timestamp("2019-01-01")


def read_csv_with_fallback(path: Path) -> tuple[pd.DataFrame, str]:
    """Read UTF-8 sources and fall back to Windows-1252 when required."""
    try:
        return pd.read_csv(path, encoding="utf-8"), "utf-8"
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp1252"), "cp1252"


def require_columns(frame: pd.DataFrame, required: set[str], source: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"{source} is missing columns: {sorted(missing)}")


def clean_calendar(raw_dir: Path) -> pd.DataFrame:
    frame, _ = read_csv_with_fallback(raw_dir / "calendar.csv")
    require_columns(
        frame,
        {
            "DateKey",
            "FullDateAlternateKey",
            "Day",
            "MonthName",
            "MonthNumberOfYear",
            "CalenderQuarter",
        },
        "calendar.csv",
    )
    frame["FullDateAlternateKey"] = pd.to_datetime(
        frame["FullDateAlternateKey"], errors="raise"
    )
    frame = frame.loc[frame["FullDateAlternateKey"] >= START_DATE].copy()
    result = pd.DataFrame(
        {
            "date_key": frame["DateKey"].astype("int64"),
            "calendar_date": frame["FullDateAlternateKey"],
            "calendar_year": frame["FullDateAlternateKey"].dt.year.astype("int64"),
            "calendar_quarter": frame["CalenderQuarter"].astype("int64"),
            "month_number": frame["MonthNumberOfYear"].astype("int64"),
            "month_name": frame["MonthName"],
            "month_short_name": frame["MonthName"].str[:3],
            "day_name": frame["Day"],
            "day_of_month": frame["FullDateAlternateKey"].dt.day.astype("int64"),
            "month_start": frame["FullDateAlternateKey"].dt.to_period("M").dt.to_timestamp(),
        }
    )
    if result["date_key"].duplicated().any():
        raise ValueError("calendar.csv contains duplicate DateKey values")
    return result.sort_values("calendar_date").reset_index(drop=True)


def clean_customers(raw_dir: Path) -> tuple[pd.DataFrame, str]:
    frame, encoding = read_csv_with_fallback(raw_dir / "customers.csv")
    require_columns(
        frame,
        {
            "CustomerKey",
            "FirstName",
            "LastName",
            "Gender",
            "DateFirstPurchase",
            "CustomerCity",
        },
        "customers.csv",
    )
    frame["DateFirstPurchase"] = pd.to_datetime(
        frame["DateFirstPurchase"], errors="raise"
    )
    gender = frame["Gender"].map({"M": "Male", "F": "Female"}).fillna("Unknown")
    result = pd.DataFrame(
        {
            "customer_key": frame["CustomerKey"].astype("int64"),
            "first_name": frame["FirstName"],
            "last_name": frame["LastName"],
            "full_name": frame["FirstName"].str.cat(frame["LastName"], sep=" "),
            "gender": gender,
            "date_first_purchase": frame["DateFirstPurchase"],
            "first_purchase_year": frame["DateFirstPurchase"].dt.year.astype("int64"),
            "customer_city": frame["CustomerCity"].fillna("Not Registered"),
        }
    )
    if result["customer_key"].duplicated().any():
        raise ValueError("customers.csv contains duplicate CustomerKey values")
    return result.sort_values("customer_key").reset_index(drop=True), encoding


def clean_products(raw_dir: Path) -> pd.DataFrame:
    frame, _ = read_csv_with_fallback(raw_dir / "products.csv")
    required = {
        "ProductKey",
        "ProductItemCode",
        "ProductName",
        "SubCategory",
        "ProductCategory",
        "ProductColor",
        "ProductSize",
        "ProductLine",
        "ProductModelName",
        "ProductDescription",
        "ProductStatus",
    }
    require_columns(frame, required, "products.csv")
    replacements = {
        "SubCategory": "sub_category",
        "ProductCategory": "product_category",
        "ProductColor": "product_color",
        "ProductSize": "product_size",
        "ProductLine": "product_line",
        "ProductModelName": "product_model_name",
        "ProductDescription": "product_description",
        "ProductStatus": "product_status",
    }
    result = pd.DataFrame(
        {
            "product_key": frame["ProductKey"].astype("int64"),
            "product_item_code": frame["ProductItemCode"],
            "product_name": frame["ProductName"],
        }
    )
    for source, target in replacements.items():
        values = frame[source].replace("NA", pd.NA)
        result[target] = values.fillna("Not Registered")
    if result["product_key"].duplicated().any():
        raise ValueError("products.csv contains duplicate ProductKey values")
    return result.sort_values("product_key").reset_index(drop=True)


def clean_sales(
    raw_dir: Path, calendar: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame, _ = read_csv_with_fallback(raw_dir / "internet_sales.csv")
    require_columns(
        frame,
        {
            "ProductKey",
            "OrderDateKey",
            "DueDateKey",
            "ShipDateKey",
            "CustomerKey",
            "SalesOrderNumber",
            "SalesAmount",
        },
        "internet_sales.csv",
    )
    frame["source_row"] = frame.index + 2
    valid_date_keys = set(calendar["date_key"])
    invalid_order_mask = ~frame["OrderDateKey"].isin(valid_date_keys)
    issues = frame.loc[invalid_order_mask, ["source_row", "OrderDateKey"]].copy()
    issues = issues.rename(columns={"OrderDateKey": "value"})
    issues["issue_type"] = "invalid_order_date_key"
    issues["source_file"] = "internet_sales.csv"
    issues["field"] = "OrderDateKey"
    issues["action"] = "excluded_from_fact_table"
    issues = issues[
        ["issue_type", "source_file", "source_row", "field", "value", "action"]
    ]

    valid = frame.loc[~invalid_order_mask].copy()
    result = pd.DataFrame(
        {
            "product_key": valid["ProductKey"].astype("int64"),
            "order_date_key": valid["OrderDateKey"].astype("int64"),
            "due_date_key": valid["DueDateKey"].astype("int64"),
            "ship_date_key": valid["ShipDateKey"].astype("int64"),
            "customer_key": valid["CustomerKey"].astype("int64"),
            "sales_order_number": valid["SalesOrderNumber"].astype("string"),
            "sales_amount": pd.to_numeric(valid["SalesAmount"], errors="raise"),
        }
    )
    return result.reset_index(drop=True), issues.reset_index(drop=True)


def clean_budget(raw_dir: Path) -> pd.DataFrame:
    frame = pd.read_excel(raw_dir / "sales_budget.xlsx", sheet_name="Budget")
    require_columns(frame, {"Date", "Budget"}, "sales_budget.xlsx:Budget")
    result = pd.DataFrame(
        {
            "budget_month": pd.to_datetime(frame["Date"], errors="raise"),
            "budget_amount": pd.to_numeric(frame["Budget"], errors="raise"),
        }
    )
    if result["budget_month"].duplicated().any():
        raise ValueError("sales_budget.xlsx contains duplicate budget months")
    return result.sort_values("budget_month").reset_index(drop=True)


def build_analysis(
    calendar: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    sales: pd.DataFrame,
    budget: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    dated_sales = sales.merge(
        calendar[["date_key", "calendar_date", "calendar_year", "month_start"]],
        left_on="order_date_key",
        right_on="date_key",
        how="left",
        validate="many_to_one",
    )
    monthly = (
        dated_sales.groupby("month_start", as_index=False)
        .agg(
            sales_amount=("sales_amount", "sum"),
            order_count=("sales_order_number", "nunique"),
            customer_count=("customer_key", "nunique"),
        )
        .merge(
            budget,
            left_on="month_start",
            right_on="budget_month",
            how="outer",
            validate="one_to_one",
        )
        .sort_values("month_start")
    )
    monthly["budget_variance"] = monthly["sales_amount"] - monthly["budget_amount"]
    monthly["budget_attainment"] = monthly["sales_amount"] / monthly["budget_amount"]
    monthly["coverage_status"] = "sales_and_budget"
    monthly.loc[monthly["sales_amount"].isna(), "coverage_status"] = "budget_only"
    monthly.loc[monthly["budget_amount"].isna(), "coverage_status"] = "sales_only"
    monthly = monthly.drop(columns="budget_month")

    enriched = sales.merge(
        products[["product_key", "product_name", "product_category"]],
        on="product_key",
        how="left",
        validate="many_to_one",
    ).merge(
        customers[["customer_key"]],
        on="customer_key",
        how="left",
        validate="many_to_one",
        indicator="customer_match",
    )
    category_sales = (
        enriched.groupby("product_category", dropna=False)["sales_amount"]
        .sum()
        .sort_values(ascending=False)
    )
    product_sales = (
        enriched.groupby("product_name", dropna=False)["sales_amount"]
        .sum()
        .sort_values(ascending=False)
    )
    year_sales = dated_sales.groupby("calendar_year")["sales_amount"].sum()
    complete_2020 = monthly.loc[monthly["month_start"].dt.year == 2020]
    sales_2020 = float(complete_2020["sales_amount"].sum())
    budget_2020 = float(complete_2020["budget_amount"].sum())

    summary: dict[str, object] = {
        "sales_coverage": {
            "first_date": dated_sales["calendar_date"].min().date().isoformat(),
            "last_date": dated_sales["calendar_date"].max().date().isoformat(),
            "valid_rows": int(len(sales)),
            "orders": int(sales["sales_order_number"].nunique()),
            "customers": int(sales["customer_key"].nunique()),
        },
        "total_sales": round(float(sales["sales_amount"].sum()), 2),
        "sales_by_year": {
            str(int(year)): round(float(amount), 2)
            for year, amount in year_sales.items()
        },
        "budget_2020": {
            "sales": round(sales_2020, 2),
            "budget": round(budget_2020, 2),
            "variance": round(sales_2020 - budget_2020, 2),
            "attainment": round(sales_2020 / budget_2020, 6),
            "months_at_or_above_budget": int(
                (complete_2020["budget_variance"] >= 0).sum()
            ),
        },
        "top_category": {
            "name": str(category_sales.index[0]),
            "sales": round(float(category_sales.iloc[0]), 2),
            "share": round(float(category_sales.iloc[0] / category_sales.sum()), 6),
        },
        "top_product": {
            "name": str(product_sales.index[0]),
            "sales": round(float(product_sales.iloc[0]), 2),
        },
        "relationship_checks": {
            "unmatched_product_rows": int(enriched["product_name"].isna().sum()),
            "unmatched_customer_rows": int(
                (enriched["customer_match"] == "left_only").sum()
            ),
        },
        "scope_note": (
            "Budget continues through 2021-06 while sales end on 2021-01-28. "
            "Budget performance conclusions use the complete 2020 calendar year."
        ),
    }
    return monthly.reset_index(drop=True), summary


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")


def build(raw_dir: Path, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    calendar = clean_calendar(raw_dir)
    customers, customer_encoding = clean_customers(raw_dir)
    products = clean_products(raw_dir)
    sales, issues = clean_sales(raw_dir, calendar)
    budget = clean_budget(raw_dir)
    monthly, summary = build_analysis(calendar, customers, products, sales, budget)

    outputs = {
        "dim_calendar.csv": calendar,
        "dim_customers.csv": customers,
        "dim_products.csv": products,
        "fact_internet_sales.csv": sales,
        "fact_budget.csv": budget,
        "analysis_monthly_sales_budget.csv": monthly,
        "data_quality_issues.csv": issues,
    }
    for filename, frame in outputs.items():
        write_csv(frame, output_dir / filename)

    summary["data_quality"] = {
        "excluded_rows": int(len(issues)),
        "issue_types": issues["issue_type"].value_counts().to_dict(),
        "customers_source_encoding": customer_encoding,
    }
    (output_dir / "kpi_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    result = build(arguments.raw_dir, arguments.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
