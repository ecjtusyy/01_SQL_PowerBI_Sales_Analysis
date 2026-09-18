# Power BI 重建说明

`upstream_sales_dashboard.pbix` 是参考仓库中的原始文件，仅用于核对原项目模型和视觉布局，不应作为本项目的原创成果展示。

## 建议的数据模型

在 Power BI 中导入 `data/processed` 下的 5 张模型表，并建立以下单向一对多关系：

- `Dim_Calendar[date_key]` → `Fact_Internet_Sales[order_date_key]`
- `Dim_Customers[customer_key]` → `Fact_Internet_Sales[customer_key]`
- `Dim_Products[product_key]` → `Fact_Internet_Sales[product_key]`
- `Dim_Calendar[month_start]` → `Fact_Budget[budget_month]`

将 `Dim_Calendar` 标记为日期表，日期列选择 `calendar_date`。`month_short_name` 必须按 `month_number` 排序。

## 作品集版页面

### 1. Executive Overview

- KPI：Total Sales、Budget Amount、Budget Variance、Budget Attainment %、Order Count、Average Order Value。
- 折线/簇状柱图：按月比较 Sales 与 Budget。
- 条形图：Top 10 Product、Top 10 Customer。
- 筛选器：Year、Month、Product Category、Customer City。
- 页面提示：2021 销售数据仅到 1 月 28 日，完整预算比较限定在 2020 年。

### 2. Product Performance

- 品类销售额与销售占比。
- 产品销售额、订单数、平均订单金额。
- Top/Bottom N 产品表，保留产品品类筛选上下文。

### 3. Customer Analysis

- 城市销售分布。
- 客户销售排名和复购订单数。
- 客户明细下钻，不在公开截图中展示不必要的个人信息。

## DAX

将 `dax/measures.dax` 中的度量值添加到单独的 `Measures` 表。先核对 2020 年 KPI：

- Sales：16,351,550.34
- Budget：15,300,000.00
- Variance：1,051,550.34
- Attainment：106.9%
- 达标月份：8/12

这些数字来自项目脚本，不是手工写入 Dashboard 的常量。

## 刷新与核对

1. 运行 `python src/build_dataset.py`。
2. 在 Power BI 中刷新全部查询。
3. 使用 `data/processed/kpi_summary.json` 核对卡片值。
4. 检查 2021-02 至 2021-06 不显示为“0 销售”，而是明确标注为缺少销售覆盖。
5. 运行 `python src/validate_project.py` 后再提交 PBIX。
