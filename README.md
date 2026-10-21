# Enterprise Sales, Profitability & Demand Intelligence

A reproducible portfolio project combining **Python, SQL, SAP Datasphere and SAP Analytics Cloud**. Fictional business: Meridian Commercial Supplies. Currency: GBP. Observed period: January 2023–December 2025. Forecast: January–March 2026. These fixed historical demo dates are intentional.

**Start here: [START_HERE.md](START_HERE.md)** — copy/paste commands and a two-hour deployment checklist.

## Delivered and verified

- Reproducible seed-42 synthetic dataset: 17,214 single-line orders, eight products, four regions, 160 customers, 36 months.
- SQLite warehouse and SQL transformations with ten automated data checks plus aggregate reconciliation.
- Forecast pipeline: last-value naive, seasonal naive, annual seasonal regression with trend; chronological train/validation/test split and series-level selection.
- Prepared CSV outputs, forecast error metrics, stock pressure signals, annual inventory turnover and a business recommendation.
- Datasphere SELECT statements and manual semantic-model setup; SAC dashboard build specification.
- Local dashboard image (a preview, not an exported SAC story).

**SAP deployment status:** source and instructions prepared; not deployed or tested in a SAP tenant. A compatible Datasphere space, SAC access and live connection permissions are prerequisites. No importable SAC story package or Datasphere transport is claimed.

## Run

```bash
python -m pip install -r requirements.txt
python src/run_project.py
```

See `docs/FORECAST_METHOD.md`, `docs/DATA_DICTIONARY.md`, `docs/DATASPHERE.md`, `docs/SAC_DASHBOARDS.md`, and `docs/GITHUB.md`.

## Architecture

Raw CSVs → SQL order/cost validation → sales facts → monthly product/region panel → Python forecasts → CSV upload back to Datasphere → analytic models → SAC story.

Sales line, cost line, monthly stock and regional targets are modelled separately. Only preaggregated compatible grains are joined. Regional targets are never repeated across product rows.

## Evidence

`outputs/validation.json`, `outputs/forecast_metrics.csv`, `outputs/BUSINESS_FINDINGS.md`, `outputs/product_profitability.csv`, `outputs/dashboard_preview.png`. Add your own SAP model and SAC story screenshots after deployment. All figures are synthetic and must be described as such in a CV or interview.
