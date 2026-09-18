# 数据字典

## Dim_Calendar

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `date_key` | integer | `YYYYMMDD` 日期键 |
| `calendar_date` | date | 公历日期 |
| `calendar_year` | integer | 年 |
| `calendar_quarter` | integer | 季度 1–4 |
| `month_number` | integer | 月份 1–12 |
| `month_name` | text | 完整英文月份名 |
| `month_short_name` | text | 三字符月份名 |
| `day_name` | text | 英文星期名称；源字段 `Day` 的真实含义 |
| `day_of_month` | integer | 月内日序号 |
| `month_start` | date | 月初日期，用于连接预算表 |

## Dim_Customers

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `customer_key` | integer | 客户主键 |
| `first_name` / `last_name` | text | 客户姓名字段 |
| `full_name` | text | 姓名拼接展示字段 |
| `gender` | text | Male、Female 或 Unknown |
| `date_first_purchase` | date | 首次购买日期 |
| `first_purchase_year` | integer | 首购年份 |
| `customer_city` | text | 客户城市 |

## Dim_Products

包含产品编码、名称、品类、子品类、颜色、尺寸、产品线、型号、描述和状态。缺失属性统一为 `Not Registered`，不会被误写为空字符串。

## Fact_Internet_Sales

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `product_key` | integer | 产品外键 |
| `order_date_key` | integer | 下单日期外键 |
| `due_date_key` | integer | 到期日期键 |
| `ship_date_key` | integer | 发货日期键 |
| `customer_key` | integer | 客户外键 |
| `sales_order_number` | text | 销售订单号；一个订单可包含多行 |
| `sales_amount` | decimal | 明细销售额 |

## Fact_Budget

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `budget_month` | date | 月初日期 |
| `budget_amount` | decimal | 月度预算金额 |
