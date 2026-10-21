# Business findings — synthetic demonstration

Revenue: £12,958,966.38; gross profit: £4,261,084.72; weighted margin: 32.9%.

Highest total product profit: Laptop.

Mean per-series test MAE for validation-selected models: 4.51 units.

                 TEST_MAE  TEST_RMSE
MODEL                               
naive           19.822917  20.971452
seasonal_naive   6.791667   7.725066
seasonal_trend   4.514458   5.242674

9 product/region pairs have December stock below January predicted demand. Review replenishment and lead times before buying.

Laptop cost inflation and promotional discounts were deliberately injected from July 2025: investigate discount policy and supplier terms. These are known simulation mechanisms, not causal discoveries from real business evidence.

Inventory flags ignore incoming purchases, lead times, safety stock, backorders and service-level targets. Forecasts estimate observed sales, not unconstrained demand. No confidence intervals or production deployment are claimed.
