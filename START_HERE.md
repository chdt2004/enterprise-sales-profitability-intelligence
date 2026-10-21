# Your two-hour build guide

The code, data and computed outputs are already included. You can upload CSVs immediately; running Python recreates everything. SAP steps require your existing tenant access. If login, roles or a live connection are unavailable, finish the local project and use the SAC CSV fallback; describe that integration accurately.

## 0–15 minutes: download, extract, run

Extract the ZIP. Open the `enterprise-intelligence` folder in VS Code: File → Open Folder. Open Terminal → New Terminal. It must be in the folder containing `requirements.txt`.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\run_project.py
```

Mac/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/run_project.py
```

Expected results: revenue **£12,958,966.38**, gross profit **£4,261,084.72**, margin **32.88%**, all failure counts zero. Open `outputs/dashboard_preview.png` and `outputs/BUSINESS_FINDINGS.md`.

Do not paste Python into SAP or SQL into PowerShell. Each Datasphere file goes into its own SQL view editor as described below.

## 15–50 minutes: Datasphere core

Follow `docs/DATASPHERE.md`, especially the fast path:

1. Import `PRODUCTS`, `CUSTOMERS`, `COSTS`, `ORDERS`, `REGIONS`, `DATES` from `data/raw` and `FORECAST`, `STOCK_POSITION` from `data/processed`.
2. Use exactly those uppercase technical names; ensure matching column types.
3. Create SQL views in this order: `V_SALES_DETAIL`, `V_MONTHLY`, `V_DASHBOARD_PANEL`, `V_STOCK_POSITION`.
4. Paste matching files in `datasphere/`; save and deploy each.
5. Create product and region dimensions and associate them with the panel.
6. Mark panel and stock views as Facts; create and deploy `AM_COMMERCIAL` and `AM_STOCK` analytic models.

If time remains import `INVENTORY`, `TARGETS` and create remaining views. This adds separate inventory/cost facts and regional target reporting. They are part of the full design; don't claim them deployed until done.

## 50–100 minutes: SAC

Follow `docs/SAC_DASHBOARDS.md`. Use the existing Datasphere live connection to `AM_COMMERCIAL`, `AM_STOCK`. Build Product Explorer first: product/region filters, revenue/profit KPIs, sales history, demand actual/forecast line chart, and December stock table.

For a tenant with no live access: import `DASHBOARD_PANEL.csv` and `STOCK_POSITION.csv` into SAC as separate models. This creates a Python/SQL → CSV → SAC route; Datasphere is demonstrated separately. Do not call this a live Datasphere integration.

## 100–115 minutes: targets, evidence

Add regional targets page if feasible; otherwise clearly label it pending. Read all business findings. Save screenshots of Datasphere objects, analytic preview and SAC pages to a new `evidence/` directory. Do not include personal or account information.

## 115–120 minutes: GitHub

Use `docs/GITHUB.md`. Create an empty GitHub repository, then copy the commands with your actual repository URL. The ZIP is not a substitute for committing extracted files.

## What to say in an interview

“I built a reproducible sales and profitability analytics pipeline using synthetic enterprise data. SQL reconciles line revenue and joins time-dependent costs, Python evaluates demand forecasts on chronological holdouts, and I prepared Datasphere fact/dimension models and SAC dashboards.”

After you actually deploy, replace “prepared” with “deployed.” Discuss stock flags as screening indicators and gross profit as revenue less product cost, not net profit.
