# SAC dashboard build: executive performance and Product Explorer

This is a build specification, not an importable SAC story. It requires manual chart creation in your SAC tenant. No local code can generate a valid tenant story package without that tenant's objects and metadata.

## Connect or import

Preferred: Stories → Create story (Optimized Design Experience where available) → add data → existing Datasphere live connection → AM_COMMERCIAL. Add AM_STOCK and AM_TARGETS as additional data sources when needed. Labels vary by release.

CSV fallback: create a model from a local file, select `data/processed/DASHBOARD_PANEL.csv`. Review types before finishing. Dimensions: MONTH (date), PRODUCT_ID, PRODUCT_NAME, CATEGORY, REGION, PHASE, MODEL. Measures: QUANTITY, REVENUE, COGS, GROSS_PROFIT, ORDER_COUNT, FORECAST_QUANTITY, ACTUAL_QUANTITY. Ignore duplicate SNAPSHOT_DATE and inventory fields for this model. Preserve null actuals for future rows. Money is GBP; margin is a percentage, not a currency. Save model as M_COMMERCIAL. Separately import STOCK_POSITION.csv as M_STOCK and REGIONAL_TARGETS.csv as M_TARGETS. Use these model names wherever the live AM names appear below.

## Calculation builder definitions

Create calculated measures via the calculation builder, selecting existing measures. Use its safe division/IF option where available, returning null for zero denominators. Formulas below are business pseudocode, not raw SAC scripting:

| Name | Calculation after aggregation | Format |
|---|---|---|
| Gross Margin | SUM(GROSS_PROFIT) / SUM(REVENUE) | 0.0% |
| Average Order Value | SUM(REVENUE) / SUM(ORDER_COUNT) | GBP 0.00 |
| Revenue Attainment | SUM(REVENUE) / SUM(SALES_TARGET) | 0.0% |
| Revenue Variance | SUM(REVENUE) − SUM(SALES_TARGET) | GBP |
| Months Cover | SUM(STOCK_QUANTITY) / SUM(FORECAST_QUANTITY) | 0.00 |

If a live model disallows the required story calculation, define it in its Datasphere analytic model. Do not average row margins or coverage. PHASE blank for early history is expected. FORECAST_QUANTITY exists only for validation, test and future months.

## Page 1: Executive Performance

Use AM_COMMERCIAL. Set page MONTH range Jan–Dec 2025. Top row: Revenue, Gross Profit, Gross Margin and Average Order Value numeric points. Second row: monthly revenue/gross-profit line chart; product gross-profit ranked bar. Third row: product table (revenue, gross profit, gross margin), region bar (gross profit). Add REGION and CATEGORY input controls, apply to all widgets on this data source. To highlight weak margins, use conditional formatting on Gross Margin below 25%. Describe 25% as an illustrative business threshold.

Create an optional AM_SALES_DETAIL chart grouped by SEGMENT. Cross-model filters require matching dimension links; apply its own date filter. AOV in this detailed model must use distinct ORDER_ID, not line count. The panel ORDER_COUNT measure is simpler for this dataset.

## Page 2: Product Explorer — flagship

All commercial widgets use AM_COMMERCIAL, so product/region filters work together without cross-model joins.

1. Add PRODUCT_ID and REGION input controls. Use one product and one region initially: P002 / North. Set scope to all commercial widgets on this page.
2. KPIs: Revenue, Gross Profit and Gross Margin, each restricted to Jan–Dec 2025. Set the chart-level date filters so future periods do not affect actual KPIs.
3. Sales history line: MONTH Jan 2023–Dec 2025; REVENUE.
4. Demand line: MONTH Jan 2025–Mar 2026, measures QUANTITY and FORECAST_QUANTITY. Actuals stop Dec 2025; forecasts continue into 2026. Do not convert null future actuals to zero or connect missing values. Annotate Jan–Jun validation, Jul–Dec test, Jan–Mar future. This line intentionally uses forecast quantity alongside observed sales; ACTUAL_QUANTITY is the evaluation-only field.
5. Product margin table: MONTH and Gross Margin, Jul–Dec 2025. A revenue/gross-profit comparison reveals margin pressure.
6. Add a stock table from AM_STOCK: PRODUCT_NAME, REGION, STOCK_QUANTITY, FORECAST_QUANTITY, STOCK_GAP, RISK. Fix snapshot to Dec 2025 and label forecast as Jan 2026. The stock model is already snapshot-only.
7. To make the same product/region selectors filter AM_STOCK, link the equivalent PRODUCT_ID and REGION dimensions across models using the story's linked dimension/filter across models facilities. In input-control settings include the stock widgets. Test P002/North and P006/West. If your tenant doesn't support the link, add explicitly labelled stock product and stock region controls; do not claim one selector controls both.
8. Commercial and stock widgets share only product/region filters. Do not apply the commercial time-range control to stock dates: commercial MONTH can be 2026 while stock is December 2025.

Acceptance check: selecting P002 / North updates every intended commercial widget, and the stock table displays exactly the same product and region. P006 has potential excess stock. The margin-pressure example is P001 in Jul–Dec 2025. Demand chart changes with either selector. If linked filtering fails, troubleshoot or disclose the separate stock selectors.

## Page 3: Regional Targets

Use only AM_TARGETS (or M_TARGETS). Page filter MONTH Jan–Dec 2025, REGION optional. Numeric points: revenue, sales target, revenue variance and revenue attainment. Clustered columns: actual revenue versus sales target by MONTH or REGION. Table by MONTH and REGION: revenue, target, variance, Gross Margin and margin target (30%). Add margin target as a constant 0.30 reference line for this synthetic dataset; never SUM MARGIN_TARGET. Show revenue variance red below zero. Product filter must not apply here because targets have no product allocation.

## Page 4 optional: Stock Pressure

AM_STOCK; snapshot Dec 2025. Table by product and region: current quantity, next-month forecast, gap, RISK, Months Cover. Conditional colours red Potential shortage, amber Potential excess, green Balanced. A bar chart of STOCK_GAP shows units; don't add gaps for different snapshots. This is a one-month screening signal, not a procurement recommendation.

## Visual polish and evidence

Use a white canvas, navy titles, teal actuals, orange forecasts and red exceptions. Put units, time ranges and “Synthetic demonstration” in each page subtitle. Save story as `Enterprise Commercial Intelligence`.

Capture screenshots after actual deployment. Do not represent `outputs/dashboard_preview.png` as an SAC screenshot. Record whether the story uses live Datasphere or CSV models in README. Capture error metric CSV and validation output as additional evidence.

## Official references

- https://help.sap.com/docs/SAP_ANALYTICS_CLOUD/18850a0e13944f53aa8a8b7c094ea29e/4951496a66054bb7b0a0b5e66232c059.html
- https://help.sap.com/docs/SAP_ANALYTICS_CLOUD/18850a0e13944f53aa8a8b7c094ea29e/90e079eac7ff416daaab96346d830c48.html
- https://help.sap.com/docs/SAP_ANALYTICS_CLOUD/00f68c2e08b941f081002fd3691d86a7/ad4281e2875949f0b4d45d1072ff4c38.html
