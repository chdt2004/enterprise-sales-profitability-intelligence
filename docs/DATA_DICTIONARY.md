# Data, grain and business definitions

## Provenance

Every record is generated locally by `src/run_project.py`, NumPy RNG seed 42. No real customers or proprietary data. `requirements.txt` declares compatible dependency ranges; exact tested versions are in `outputs/environment.txt`. Orders are simulated with trend, annual seasonality, product/region differences and random variation. Laptop discounts and costs deliberately rise from July 2025. Monitor/North stock is deliberately low; cabinet stock is deliberately high. Inventory snapshots are independently simulated, not a reconciled stock movement ledger.

## Raw tables

| Table | Primary grain/key | Fields and units |
|---|---|---|
| ORDERS | ORDER_ID + LINE_ID | ORDER_DATE, MONTH (first day), PRODUCT_ID, CUSTOMER_ID; QUANTITY units; SELLING_PRICE GBP/unit; DISCOUNT fraction 0–1 |
| PRODUCTS | PRODUCT_ID | PRODUCT_NAME, CATEGORY, LIST_PRICE GBP, SUPPLIER |
| CUSTOMERS | CUSTOMER_ID | SEGMENT, REGION; no history tracking in this demo |
| COSTS | PRODUCT_ID + MONTH | UNIT_COST GBP; monthly effective unit cost |
| INVENTORY | PRODUCT_ID + REGION + MONTH | SNAPSHOT_DATE month end; STOCK_QUANTITY units; REORDER_LEVEL units |
| TARGETS | MONTH + REGION | SALES_TARGET GBP; MARGIN_TARGET fraction; synthetic independently specified plan |
| REGIONS | REGION | Four regional keys |
| DATES | DATE | Daily dates; MONTH first-day key |

## Processed tables

- SALES_DETAIL: order line with customer/product attributes and matched month cost.
- MONTHLY_SALES: month/product/region sales fact; additive currency, quantity and order counts for this one-line-order dataset.
- FORECAST: month/product/region; validation Jan–Jun 2025, test Jul–Dec 2025, future Jan–Mar 2026. PHASE gives the authoritative classification. Model chosen on Jan–Jun 2025 validation. Historical months before Jan 2025 have no forecast.
- DASHBOARD_PANEL: 1,248 month/product/region rows (39 × 8 × 4); outer join preserves future forecasts. Actual measures are null in future rows. Inventory exists only for historical rows; use STOCK_POSITION for snapshot KPIs.
- STOCK_POSITION: 32 rows at December 2025, enriched with January 2026 demand. RISK and STOCK_GAP are screening metrics.
- REGIONAL_TARGETS: month/region actual revenue, gross profit, target and variance. No product or customer granularity.
- INVENTORY_TURNOVER: product/region annual 2025 COGS divided by average of twelve month-end stock valuations.

## Metrics

Revenue = SUM(line quantity × selling price × (1 − discount), rounded per line). Excludes tax, refunds and shipping. COGS = SUM(quantity × matching monthly unit cost, rounded per line). Gross profit = revenue − COGS. Margin = SUM(gross profit) / SUM(revenue); never average row percentages. AOV = revenue / distinct order count; all simulated orders have one line. If extended to multi-line orders, do not sum preaggregated distinct counts across products.

Inventory turnover = annual COGS / average monthly ending inventory value, in turns/year. Closing inventory is additive across products and regions, never across dates. Regional margin targets are nonadditive percentages; in this dataset they are uniformly 30%; filter to one month/region when presenting them or explicitly define an aggregate target policy.

Months cover = December closing quantity / January demand forecast. Negative stock gap means a potential shortage assuming no receipts and a one-month horizon. Above two months cover is a configurable potential excess indicator. Reorder level is provided for comparison, not a calculated optimal policy.

No operating expenses, net profit, VAT, returns, stock movements or supply lead times are modelled. Gross profit should not be called net profit. Revenue growth can coexist with a falling gross margin.
