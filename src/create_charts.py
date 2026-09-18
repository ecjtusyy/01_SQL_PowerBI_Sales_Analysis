"""Create lightweight SVG portfolio previews from the processed data."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
IMAGE_DIR = PROJECT_ROOT / "images"
NAVY = "#16324F"
BLUE = "#2F80ED"
ORANGE = "#F2994A"
LIGHT = "#E8EEF5"
MUTED = "#60758A"


def svg_text(
    x: float,
    y: float,
    text: str,
    *,
    size: int = 14,
    fill: str = NAVY,
    weight: int = 400,
    anchor: str = "start",
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}">{escape(text)}</text>'
    )


def sales_vs_budget() -> None:
    monthly = pd.read_csv(
        PROCESSED_DIR / "analysis_monthly_sales_budget.csv",
        parse_dates=["month_start"],
    )
    data = monthly.loc[monthly["month_start"].dt.year == 2020].copy()
    width, height = 1200, 650
    left, right, top, bottom = 90, 40, 90, 120
    plot_width = width - left - right
    plot_height = height - top - bottom
    maximum = 2_000_000
    slot = plot_width / len(data)
    bar_width = slot * 0.31
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
        svg_text(left, 42, "2020 monthly sales vs budget", size=26, weight=700),
        svg_text(left, 68, "Complete calendar-year comparison", size=14, fill=MUTED),
    ]
    for tick in range(0, maximum + 1, 500_000):
        y = top + plot_height - tick / maximum * plot_height
        elements.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" stroke="{LIGHT}"/>'
        )
        elements.append(svg_text(left - 12, y + 5, f"{tick / 1_000_000:.1f}M", size=12, fill=MUTED, anchor="end"))

    for index, row in data.reset_index(drop=True).iterrows():
        center = left + slot * (index + 0.5)
        sales_height = float(row["sales_amount"]) / maximum * plot_height
        budget_height = float(row["budget_amount"]) / maximum * plot_height
        elements.extend(
            [
                f'<rect x="{center-bar_width-2:.1f}" y="{top+plot_height-sales_height:.1f}" width="{bar_width:.1f}" height="{sales_height:.1f}" rx="2" fill="{BLUE}"/>',
                f'<rect x="{center+2:.1f}" y="{top+plot_height-budget_height:.1f}" width="{bar_width:.1f}" height="{budget_height:.1f}" rx="2" fill="{ORANGE}"/>',
                svg_text(center, top + plot_height + 25, row["month_start"].strftime("%b"), size=12, fill=MUTED, anchor="middle"),
            ]
        )

    elements.extend(
        [
            f'<rect x="{left}" y="{height-74}" width="14" height="14" rx="2" fill="{BLUE}"/>',
            svg_text(left + 22, height - 62, "Sales", size=13),
            f'<rect x="{left+90}" y="{height-74}" width="14" height="14" rx="2" fill="{ORANGE}"/>',
            svg_text(left + 112, height - 62, "Budget", size=13),
            svg_text(
                width - right,
                height - 62,
                "Sales 16.35M | Budget 15.30M | Variance +1.05M | Attainment 106.9%",
                size=13,
                fill=NAVY,
                weight=700,
                anchor="end",
            ),
            "</svg>",
        ]
    )
    (IMAGE_DIR / "sales_vs_budget_2020.svg").write_text(
        "\n".join(elements), encoding="utf-8"
    )


def category_mix() -> None:
    sales = pd.read_csv(PROCESSED_DIR / "fact_internet_sales.csv")
    products = pd.read_csv(PROCESSED_DIR / "dim_products.csv")
    data = (
        sales.merge(products[["product_key", "product_category"]], on="product_key")
        .groupby("product_category", as_index=False)["sales_amount"]
        .sum()
        .sort_values("sales_amount", ascending=False)
        .reset_index(drop=True)
    )
    total = float(data["sales_amount"].sum())
    maximum = float(data["sales_amount"].max())
    width, height = 1000, 460
    left, right, top = 180, 140, 110
    plot_width = width - left - right
    row_height = 82
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#FFFFFF"/>',
        svg_text(55, 42, "Sales by product category", size=26, weight=700),
        svg_text(55, 68, "Share of total valid sales", size=14, fill=MUTED),
    ]
    for index, row in data.iterrows():
        y = top + index * row_height
        bar_width = float(row["sales_amount"]) / maximum * plot_width
        share = float(row["sales_amount"]) / total
        elements.extend(
            [
                svg_text(left - 18, y + 24, str(row["product_category"]), size=15, weight=600, anchor="end"),
                f'<rect x="{left}" y="{y}" width="{plot_width}" height="32" rx="4" fill="{LIGHT}"/>',
                f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="32" rx="4" fill="{BLUE}"/>',
                svg_text(left + bar_width + 12, y + 23, f"{share:.1%}", size=14, weight=700),
                svg_text(left, y + 55, f"{float(row['sales_amount']) / 1_000_000:.2f}M", size=12, fill=MUTED),
            ]
        )
    elements.append("</svg>")
    (IMAGE_DIR / "sales_by_category.svg").write_text(
        "\n".join(elements), encoding="utf-8"
    )


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    sales_vs_budget()
    category_mix()
    print(f"Created SVG preview charts in {IMAGE_DIR}")


if __name__ == "__main__":
    main()
