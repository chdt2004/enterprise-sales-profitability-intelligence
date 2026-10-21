# Forecasting methodology

32 independent product/region series, each with 36 monthly nonzero sales observations. Training Jan 2023–Dec 2024 (24 months); validation Jan–Jun 2025 (6); final test Jul–Dec 2025 (6). Monthly aggregation happens before modelling. No random split.

Candidates:
1. Last-value naive: repeat the most recent observed value for the whole horizon.
2. Seasonal naive: same month last year.
3. Seasonal trend regression: least-squares intercept, linear month trend, annual sine and cosine; negative predictions clipped to zero.

Select minimum validation MAE per series, refit on 30 months, and evaluate on six untouched test months. Report every candidate for comparison; test performance does not select the winning model. Refit selected model on all 36 observations to forecast Jan–Mar 2026. `FORECAST.csv` includes selected model validation predictions made from 24 months, test predictions made from 30 months, and future predictions made from 36 months. Validation curves are used for model selection and must not be described as independent test results.

MAE = mean absolute unit error; RMSE = square root of mean squared unit error. `forecast_metrics.csv` stores per-series values; reported average RMSE is the average of per-series RMSEs, not pooled RMSE. Aggregated regional error requires aggregating predictions/actuals first and recomputing errors. No claim of universal improvement over baseline.

Limitations: short synthetic history, no rolling-origin assessment, no interval calibration, no exogenous inputs, no promotions as forecast features, no intermittent-demand treatment, no lost-sales correction. Do not infer real-world accuracy from these scores. Regression is deliberately modest enough for 24 training observations. Demand means observed sales here; real stockouts would bias that proxy.

Run `python src/run_project.py`, inspect `outputs/forecast_metrics.csv`, then open `notebooks/analysis.ipynb` for an optional review wrapper. The executable forecasting implementation is the documented Python source; a notebook rerun requires Jupyter installed separately.
