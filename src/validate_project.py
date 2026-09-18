"""Run reproducibility and reconciliation checks for the processed dataset."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def assert_close(actual: float, expected: float, tolerance: float = 0.01) -> None:
    if abs(actual - expected) > tolerance:
        raise AssertionError(f"expected {expected}, got {actual}")


def main() -> None:
    calendar = pd.read_csv(PROCESSED_DIR / "dim_calendar.csv")
    customers = pd.read_csv(PROCESSED_DIR / "dim_customers.csv")
    products = pd.read_csv(PROCESSED_DIR / "dim_products.csv")
    sales = pd.read_csv(PROCESSED_DIR / "fact_internet_sales.csv")
    monthly = pd.read_csv(
        PROCESSED_DIR / "analysis_monthly_sales_budget.csv",
        parse_dates=["month_start"],
    )
    issues = pd.read_csv(PROCESSED_DIR / "data_quality_issues.csv")
    summary = json.loads((PROCESSED_DIR / "kpi_summary.json").read_text("utf-8"))

    if calendar["date_key"].duplicated().any():
        raise AssertionError("dim_calendar contains duplicate keys")
    if customers["customer_key"].duplicated().any():
        raise AssertionError("dim_customers contains duplicate keys")
    if products["product_key"].duplicated().any():
        raise AssertionError("dim_products contains duplicate keys")
    if not sales["product_key"].isin(products["product_key"]).all():
        raise AssertionError("fact table contains unmatched product keys")
    if not sales["customer_key"].isin(customers["customer_key"]).all():
        raise AssertionError("fact table contains unmatched customer keys")
    if not sales["order_date_key"].isin(calendar["date_key"]).all():
        raise AssertionError("fact table contains unmatched order date keys")
    if len(issues) != 2 or set(issues["value"]) != {20190229}:
        raise AssertionError("expected two audited rows with invalid date key 20190229")

    assert_close(float(sales["sales_amount"].sum()), summary["total_sales"])
    year_2020 = monthly.loc[monthly["month_start"].dt.year == 2020]
    assert_close(
        float(year_2020["sales_amount"].sum()), summary["budget_2020"]["sales"]
    )
    assert_close(
        float(year_2020["budget_amount"].sum()), summary["budget_2020"]["budget"]
    )
    if len(year_2020) != 12:
        raise AssertionError("2020 comparison must contain 12 complete months")

    print(
        "PASS: keys, relationships, audited exclusions, KPI totals and the "
        "12-month 2020 budget comparison reconcile."
    )


if __name__ == "__main__":
    main()
