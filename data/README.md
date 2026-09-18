# 数据说明

## 数据来源

原始文件来自公开参考仓库 [khaled-gohar/SQL_PBI_SalesAnalysis](https://github.com/khaled-gohar/SQL_PBI_SalesAnalysis)，本地快照获取日期为 2026-09-17。

`data/raw` 保留用于复现的源文件：

| 文件 | 作用 | 记录数/范围 |
| --- | --- | --- |
| `calendar.csv` | 日期维表 | 1,096 行 |
| `customers.csv` | 客户维表 | 18,484 行；Windows-1252 编码 |
| `products.csv` | 产品维表 | 606 行 |
| `internet_sales.csv` | 销售事实表 | 58,168 行 |
| `sales_budget.xlsx` | 月度预算 | 2020-01 至 2021-06，共 18 个月 |

## 获取方式

1. 打开上面的参考仓库并下载源码归档。
2. 将 `Original_Data` 中的文件复制到 `data/raw`。
3. 按本项目命名改为小写蛇形格式，或通过 `--raw-dir` 指向相同结构的数据目录。
4. 执行 `python src/build_dataset.py` 生成 `data/processed`。

不要从 README 截图反推数据，也不要把 Power BI 发布页中的汇总值当作原始数据。

## 处理规则

- 统一字段为 `snake_case`，日期输出为 ISO `YYYY-MM-DD`。
- 将产品属性中的空值和 `NA` 统一为 `Not Registered`。
- 客户维表保留全部客户；只按首购年份过滤会破坏销售事实表的外键匹配。
- 将客户文件的 Windows-1252 编码转换为 UTF-8 with BOM，避免 Power BI 中文环境导入乱码。
- 销售事实表通过 `order_date_key` 与日期维表做完整性校验。
- 两行 `order_date_key = 20190229` 无法匹配真实日期，写入 `data_quality_issues.csv` 并从事实表排除。
- 预算覆盖到 2021-06，但销售只到 2021-01-28。预算达成结论限定在完整的 2020 自然年。

## 生成文件

| 文件 | Power BI 表名 | 粒度 |
| --- | --- | --- |
| `dim_calendar.csv` | `Dim_Calendar` | 每日一行 |
| `dim_customers.csv` | `Dim_Customers` | 每位客户一行 |
| `dim_products.csv` | `Dim_Products` | 每个产品一行 |
| `fact_internet_sales.csv` | `Fact_Internet_Sales` | 每条销售明细一行 |
| `fact_budget.csv` | `Fact_Budget` | 每月一行 |
| `analysis_monthly_sales_budget.csv` | 可选核对表 | 每月一行 |
| `data_quality_issues.csv` | 审计记录 | 每个问题源行一行 |
| `kpi_summary.json` | 自动验证摘要 | 单个 JSON 对象 |

## 使用限制

参考仓库快照中没有 `LICENSE` 文件。不要假设原始数据、SQL 或 PBIX 可以公开再授权；公开发布前应取得原作者许可，或替换为具有明确授权的数据与自行重建的 Power BI 文件。详见根目录 `NOTICE.md`。
