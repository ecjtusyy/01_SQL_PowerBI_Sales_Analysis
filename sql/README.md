# SQL 使用说明

这些脚本面向 PostgreSQL 14+，按文件名前缀顺序执行。

1. 执行 `00_schema.sql` 创建 `sales_portfolio` schema 与原始表。
2. 将 `data/raw` 中的 CSV 导入对应 `raw_*` 表；预算工作表需先另存为 CSV，列名映射为 `budget_month`、`budget_amount`。
3. 执行 `01` 至 `05` 创建星型模型视图。
4. 执行 `06_data_quality_checks.sql` 检查无效日期键与维度关联。
5. 使用 `07_analysis_queries.sql` 复核月度预算差异、品类贡献和 Top 产品。

本项目同时提供 `src/build_dataset.py`，无需 PostgreSQL 即可生成 Power BI 可导入的同口径 CSV。
