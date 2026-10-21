# Datasphere: import, paste, model, deploy

These are manual tenant steps. SQL files are HANA-style SELECT bodies for **Data Builder → New SQL View → SQL (Standard Query)**, not SQLScript and not database-console CREATE VIEW statements. Do not paste the SQLite script here. UI labels can differ by tenant release.

## 1. Prerequisites

A provisioned Datasphere space, space modelling permissions, storage available, and an SAC tenant. A Datasphere trial does not by itself guarantee SAC or a working live connection. Keep credentials out of this project.

## 2. Import files and types

Data Builder → select your space → Import CSV File (sometimes under New/Import). Select a file, first row contains column names, comma delimiter, UTF-8. Use the technical table name in the table below, uppercase, without a suffix. Review schema, import data, save and deploy. Verify a nonzero preview row count.

| Local file | Technical table | Key |
|---|---|---|
| data/raw/PRODUCTS.csv | PRODUCTS | PRODUCT_ID |
| data/raw/CUSTOMERS.csv | CUSTOMERS | CUSTOMER_ID |
| data/raw/COSTS.csv | COSTS | PRODUCT_ID, MONTH |
| data/raw/ORDERS.csv | ORDERS | ORDER_ID, LINE_ID |
| data/raw/REGIONS.csv | REGIONS | REGION |
| data/raw/DATES.csv | DATES | DATE |
| data/raw/INVENTORY.csv | INVENTORY | PRODUCT_ID, REGION, MONTH |
| data/raw/TARGETS.csv | TARGETS | MONTH, REGION |
| data/processed/FORECAST.csv | FORECAST | MONTH, PRODUCT_ID, REGION |
| data/processed/STOCK_POSITION.csv | STOCK_POSITION | PRODUCT_ID, REGION |

Use NVARCHAR(40) for IDs and categorical fields (PRODUCT_NAME can be 100). Use DATE for ORDER_DATE, SNAPSHOT_DATE, MONTH and DATE in **every table**, parsing YYYY-MM-DD. Use INTEGER for order LINE_ID, raw quantities and stock. Use DECIMAL(18,2) for money; DECIMAL(9,4) for discount and target margin; DECIMAL(18,6) for forecast quantities, coverage and forecast actuals. In STOCK_POSITION allow STOCK_GAP to be negative. Preserve empty numeric cells as NULL, not zero or strings. Recheck inferred types, especially all-empty or partial forecast fields. Do not use a string month on one side of a DATE join.

Fast path imports only PRODUCTS, CUSTOMERS, COSTS, ORDERS, REGIONS, DATES, FORECAST, STOCK_POSITION. Inventory and targets can be added afterwards.

## 3. Create SQL views in dependency order

Click New SQL View, choose Standard Query, paste **the entire matching file**, set the exact technical name, validate, save, deploy. Import source tables in the same space. If an object is not found, verify its technical name and deployment; a business label is not the SQL name.

| Order | View | Source file | Purpose |
|---|---|---|---|
| 1 | DIM_PRODUCT | datasphere/DIM_PRODUCT.sql | Product dimension |
| 2 | DIM_CUSTOMER | datasphere/DIM_CUSTOMER.sql | Customer dimension |
| 3 | DIM_REGION | datasphere/DIM_REGION.sql | Region dimension |
| 4 | DIM_DATE | datasphere/DIM_DATE.sql | Daily date dimension |
| 5 | V_SALES_DETAIL | datasphere/V_SALES_DETAIL.sql | Joined order line sales/profit |
| 6 | V_MONTHLY | datasphere/V_MONTHLY.sql | Month/product/region aggregation |
| 7 | V_DASHBOARD_PANEL | datasphere/V_DASHBOARD_PANEL.sql | Actual sales + Python forecasts |
| 8 | V_STOCK_POSITION | datasphere/V_STOCK_POSITION.sql | December snapshot + January forecast risk |
| 9 | V_COST_FACT | datasphere/V_COST_FACT.sql | Separate order-line COGS fact |
| 10 | V_INVENTORY_FACT | datasphere/V_INVENTORY_FACT.sql | Monthly inventory valuations |
| 11 | V_REGIONAL_TARGETS | datasphere/V_REGIONAL_TARGETS.sql | Month/region target comparison |
| 12 | V_FORECAST | datasphere/V_FORECAST.sql | Forecast-only consumption if needed |

V_DASHBOARD_PANEL uses historical actuals joined to forecasts plus future-only forecast rows. UNION ALL deliberately excludes historical forecast rows from its second branch. It avoids joining monthly inventory to individual sales lines. Verify 1,248 panel rows, 32 stock-position rows, 1,152 monthly rows and 144 regional-target rows.

## 4. Semantic dimensions

In each DIM view, set Semantic Usage = Dimension. Mark the following identifier columns as keys:

- DIM_PRODUCT: PRODUCT_ID. Expose PRODUCT_NAME, CATEGORY, SUPPLIER as attributes.
- DIM_CUSTOMER: CUSTOMER_ID. Expose SEGMENT and REGION.
- DIM_REGION: REGION.
- DIM_DATE: DATE. MONTH is an attribute; DATE is unique, MONTH is not.

Save/deploy each. This is an ordinary daily date dimension, not a claim of a configured SAP time hierarchy.

## 5. Facts and associations

Set Semantic Usage = Fact on each V view used analytically. In the output node, define measures and associations. Associate to dimensions with many-to-one cardinality, mapping fields as below. Do not add a join that changes row counts.

| Fact | Dimension mapping | SUM measures |
|---|---|---|
| V_DASHBOARD_PANEL | PRODUCT_ID → DIM_PRODUCT.PRODUCT_ID; REGION → DIM_REGION.REGION; MONTH → DIM_DATE.DATE | REVENUE, COGS, GROSS_PROFIT, QUANTITY, ORDER_COUNT, FORECAST_QUANTITY, ACTUAL_QUANTITY |
| V_SALES_DETAIL | PRODUCT_ID → DIM_PRODUCT.PRODUCT_ID; CUSTOMER_ID → DIM_CUSTOMER.CUSTOMER_ID; REGION → DIM_REGION.REGION; ORDER_DATE → DIM_DATE.DATE | REVENUE, COGS, GROSS_PROFIT, QUANTITY |
| V_COST_FACT | Same order date/product/customer/region mappings | COGS, QUANTITY |
| V_INVENTORY_FACT | PRODUCT_ID, REGION; SNAPSHOT_DATE → DIM_DATE.DATE | STOCK_QUANTITY, INVENTORY_VALUE, REORDER_LEVEL, only within one snapshot |
| V_STOCK_POSITION | PRODUCT_ID, REGION; MONTH → DIM_DATE.DATE | STOCK_QUANTITY, FORECAST_QUANTITY, STOCK_GAP, only current snapshot |
| V_REGIONAL_TARGETS | REGION, MONTH → DIM_DATE.DATE | REVENUE, GROSS_PROFIT, SALES_TARGET, REVENUE_VARIANCE |
| V_FORECAST | PRODUCT_ID, REGION; MONTH → DIM_DATE.DATE | FORECAST_QUANTITY, ACTUAL_QUANTITY |

Expose direct descriptive attributes such as PHASE, MODEL, RISK and CATEGORY as appropriate. Coverage and percentages are ratios: create them as aggregate calculations in the analytic model or SAC; do not sum raw MONTHS_COVER or MARGIN_PCT. In stock views monthly values are semiadditive; the supplied stock dashboard fixes December 2025. Do not show a stock total across months. In full inventory models configure time exception aggregation if needed; this pack uses an explicit date filter instead.

## 6. Analytic models

Data Builder → New Analytic Model → choose deployed fact → select relevant measures and associated dimensions → save/deploy:

- AM_COMMERCIAL from V_DASHBOARD_PANEL (priority).
- AM_STOCK from V_STOCK_POSITION (priority).
- AM_SALES_DETAIL from V_SALES_DETAIL (customer segmentation).
- AM_TARGETS from V_REGIONAL_TARGETS (regional targets).
- Optional AM_COST and AM_INVENTORY from their separate fact views.

Use the current Fact → Analytic Model workflow. Do not switch to the deprecated Analytical Dataset approach to make a view appear in SAC. Ensure the analytic model is available for consumption; where your tenant shows an Expose for Consumption option, enable it on the relevant object. Tenant roles also control visibility.

Prefer aggregate calculated measures in AM_COMMERCIAL: Margin = GROSS_PROFIT / REVENUE, AOV = REVENUE / ORDER_COUNT, with zero-denominator protection. If expression syntax differs, use SAC's calculation builder to select the measures rather than pasting arbitrary SQL formulas. SAC steps provide the exact business definitions.

## 7. Reconcile and connect

Preview AM_COMMERCIAL all actual history: SUM REVENUE = 12,958,966.38; SUM GROSS_PROFIT = 4,261,084.72; SUM ORDER_COUNT = 17,214. Future rows must have NULL actual revenue/quantity. Compare a single product/region/month to MONTHLY_SALES.csv.

In SAC use or create a Live Data Connection of type SAP Datasphere with your tenant hostname and supported authentication. An administrator may need to configure trust, allowed origins or roles. Do not guess tenant URLs. If the connection is absent and you cannot create it, use CSV fallback and document the status.

## 8. Forecast refresh path

Rerun Python → replace FORECAST table data with `data/processed/FORECAST.csv` (same columns/types) → refresh story. Replace STOCK_POSITION similarly. Avoid an append operation: it duplicates keys. In this demo source data and seed are fixed, so a rerun reproduces the same business scenario. A production implementation would ingest new actuals and advance dates.

## Official references

- https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/5c1e3d4a49554fcd8fcf199d664d1109.html
- https://help.sap.com/docs/SAP_DATASPHERE/c8a54ee704e94e15926551293243fd1d/e5fbe9e2cb93484dab8b1963145e565f.html
- https://help.sap.com/docs/SAP_ANALYTICS_CLOUD/00f68c2e08b941f081002fd3691d86a7/ad4281e2875949f0b4d45d1072ff4c38.html
