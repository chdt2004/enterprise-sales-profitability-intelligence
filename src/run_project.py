"""Reproducible synthetic enterprise analytics. Run from any directory."""
from pathlib import Path
import json, sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'; OUT=ROOT/'data/processed'; REPORT=ROOT/'outputs'
for p in (RAW,OUT,REPORT): p.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(42)
months=pd.date_range('2023-01-01','2025-12-01',freq='MS')
regions=['North','South','East','West']
products=pd.DataFrame([{'PRODUCT_ID':f'P{i:03}','PRODUCT_NAME':n,'CATEGORY':c,'LIST_PRICE':p,'SUPPLIER':f'S{1+i%3}'} for i,(n,c,p) in enumerate([('Laptop','Technology',800),('Monitor','Technology',220),('Keyboard','Technology',55),('Desk','Furniture',260),('Chair','Furniture',140),('Cabinet','Furniture',180),('Paper','Office',12),('Pens','Office',8)],1)])
customers=pd.DataFrame([{'CUSTOMER_ID':f'C{i:03}','SEGMENT':['SME','Enterprise','Consumer'][i%3],'REGION':regions[i%4]} for i in range(1,161)])
costs=[]; orders=[]; inventory=[]; targets=[]; oid=0
for t,m in enumerate(months):
    for p in products.itertuples():
        cost=round(p.LIST_PRICE*(.60+.02*(t/12)+(.09 if p.PRODUCT_ID=='P001' and t>=30 else 0)),2)
        costs.append([p.PRODUCT_ID,m.strftime('%Y-%m-%d'),cost])
        for ri,r in enumerate(regions):
            demand=max(5,round((32+int(p.PRODUCT_ID[1:])*3)*(1+t*.012)*(1+.26*np.sin(2*np.pi*(m.month-1)/12))*(1+ri*.12)*rng.uniform(.9,1.1)))
            remaining=demand
            while remaining:
                qty=min(remaining,int(rng.integers(1,9))); remaining-=qty; oid+=1
                cid=rng.choice(customers.loc[customers.REGION==r,'CUSTOMER_ID'])
                discount=.16 if p.PRODUCT_ID=='P001' and t>=30 else float(rng.choice([0,.03,.05,.10]))
                day=int(rng.integers(1,m.days_in_month+1))
                orders.append([f'O{oid:06}',1,m.replace(day=day).strftime('%Y-%m-%d'),m.strftime('%Y-%m-%d'),p.PRODUCT_ID,cid,qty,p.LIST_PRICE,discount])
            stock=round(demand*(.35 if p.PRODUCT_ID=='P002' and r=='North' else 2.8 if p.PRODUCT_ID=='P006' else 1.2))
            inventory.append([p.PRODUCT_ID,r,(m+pd.offsets.MonthEnd()).strftime('%Y-%m-%d'),m.strftime('%Y-%m-%d'),stock,round(demand*.5)])
    for ri,r in enumerate(regions):
        # Independently specified synthetic plan; not derived from actual results.
        targets.append([m.strftime('%Y-%m-%d'),r,round(60000*(1+ri*.12)*(1+t*.012)*(1+.26*np.sin(2*np.pi*(m.month-1)/12)),2),.30])
tables={'PRODUCTS':products,'CUSTOMERS':customers,'COSTS':pd.DataFrame(costs,columns=['PRODUCT_ID','MONTH','UNIT_COST']), 'ORDERS':pd.DataFrame(orders,columns=['ORDER_ID','LINE_ID','ORDER_DATE','MONTH','PRODUCT_ID','CUSTOMER_ID','QUANTITY','SELLING_PRICE','DISCOUNT']), 'INVENTORY':pd.DataFrame(inventory,columns=['PRODUCT_ID','REGION','SNAPSHOT_DATE','MONTH','STOCK_QUANTITY','REORDER_LEVEL']), 'TARGETS':pd.DataFrame(targets,columns=['MONTH','REGION','SALES_TARGET','MARGIN_TARGET']), 'REGIONS':pd.DataFrame({'REGION':regions}), 'DATES':pd.DataFrame({'DATE':pd.date_range('2023-01-01','2026-03-31').strftime('%Y-%m-%d')})}
tables['DATES']['MONTH']=tables['DATES'].DATE.str[:7]+'-01'
con=sqlite3.connect(REPORT/'warehouse.sqlite')
for name,df in tables.items():
    df.to_csv(RAW/f'{name}.csv',index=False); df.to_sql(name,con,if_exists='replace',index=False)
con.executescript((ROOT/'sql/01_transformations.sql').read_text())
checks={}
for name,query in json.loads((ROOT/'sql/checks.json').read_text()).items():
    failures=pd.read_sql_query(query,con); checks[name]=len(failures)
    assert failures.empty, f'{name}: {len(failures)} failures'
sales=pd.read_sql_query('SELECT * FROM V_SALES_DETAIL',con)
monthly=pd.read_sql_query('SELECT * FROM V_MONTHLY',con)
regional=pd.read_sql_query('SELECT * FROM V_REGIONAL_TARGETS',con)
sales.to_csv(OUT/'SALES_DETAIL.csv',index=False)
monthly.to_csv(OUT/'MONTHLY_SALES.csv',index=False)
regional.to_csv(OUT/'REGIONAL_TARGETS.csv',index=False)
assert np.isclose(monthly.REVENUE.sum(),sales.REVENUE.sum(),atol=.01)
assert np.isclose(regional.REVENUE.sum(),sales.REVENUE.sum(),atol=.01)
# 24-month training, 6-month validation for selection, untouched 6-month test.
# Candidate: linear trend + annual sine/cosine, fitted only to training history.
def design(t):
    t=np.asarray(t); return np.column_stack([np.ones(len(t)),t,np.sin(2*np.pi*t/12),np.cos(2*np.pi*t/12)])
def predict(y,start,h,model):
    if model=='naive': return np.repeat(y[-1],h)
    if model=='seasonal_naive': return np.array([y[(start+i)-12] if (start+i)-12<len(y) else y[-12+((start+i)%12)] for i in range(h)])
    return np.maximum(0,design(np.arange(start,start+h))@np.linalg.lstsq(design(np.arange(len(y))),y,rcond=None)[0])
models=['naive','seasonal_naive','seasonal_trend']; forecasts=[]; metrics=[]
for (pid,region),g in monthly.groupby(['PRODUCT_ID','REGION']):
    g=g.sort_values('MONTH'); y=g.QUANTITY.to_numpy(float)
    val={model:float(np.mean(np.abs(y[24:30]-predict(y[:24],24,6,model)))) for model in models}
    chosen=min(val,key=val.get)
    for model in models:
        pred=predict(y[:30],30,6,model)
        metrics.append([pid,region,model,val[model],float(np.mean(np.abs(y[30:]-pred))),float(np.sqrt(np.mean((y[30:]-pred)**2))),int(model==chosen)])
    for phase,start,h,history in [('Validation',24,6,y[:24]),('Test',30,6,y[:30]),('Future',36,3,y)]:
        pred=predict(history,start,h,chosen)
        for j,v in enumerate(pred):
            dt=pd.Timestamp('2023-01-01')+pd.DateOffset(months=start+j)
            forecasts.append([dt.strftime('%Y-%m-%d'),pid,region,phase,chosen,float(v),float(y[start+j]) if start+j<36 else None])
f=pd.DataFrame(forecasts,columns=['MONTH','PRODUCT_ID','REGION','PHASE','MODEL','FORECAST_QUANTITY','ACTUAL_QUANTITY'])
metrics=pd.DataFrame(metrics,columns=['PRODUCT_ID','REGION','MODEL','VALIDATION_MAE','TEST_MAE','TEST_RMSE','SELECTED'])
f.to_csv(OUT/'FORECAST.csv',index=False); metrics.to_csv(REPORT/'forecast_metrics.csv',index=False)
# Monthly panel joins only unique month/product/region records; inventory stays a snapshot.
panel=monthly.merge(f,on=['MONTH','PRODUCT_ID','REGION'],how='outer',validate='one_to_one')
panel=panel.merge(tables['INVENTORY'],on=['MONTH','PRODUCT_ID','REGION'],how='left',validate='one_to_one')
panel=panel.merge(products[['PRODUCT_ID','PRODUCT_NAME','CATEGORY']],on='PRODUCT_ID',validate='many_to_one')
panel['MARGIN_PCT']=panel.GROSS_PROFIT/panel.REVENUE
panel.to_csv(OUT/'DASHBOARD_PANEL.csv',index=False)
latest=monthly[monthly.MONTH=='2025-12-01'].merge(tables['INVENTORY'][tables['INVENTORY'].MONTH=='2025-12-01'],on=['MONTH','PRODUCT_ID','REGION'],validate='one_to_one')
nextmonth=f[(f.MONTH=='2026-01-01')&(f.PHASE=='Future')][['PRODUCT_ID','REGION','FORECAST_QUANTITY']]
stock=latest.merge(nextmonth,on=['PRODUCT_ID','REGION'],validate='one_to_one').merge(products[['PRODUCT_ID','PRODUCT_NAME','CATEGORY']],on='PRODUCT_ID',validate='many_to_one')
stock['MONTHS_COVER']=stock.STOCK_QUANTITY/stock.FORECAST_QUANTITY
stock['STOCK_GAP']=stock.STOCK_QUANTITY-stock.FORECAST_QUANTITY
stock['RISK']=np.where(stock.STOCK_QUANTITY<stock.FORECAST_QUANTITY,'Potential shortage',np.where(stock.MONTHS_COVER>2,'Potential excess','Balanced'))
# Annual COGS / average of twelve month-end inventory values at matching monthly costs.
inv=tables['INVENTORY'].merge(tables['COSTS'],on=['PRODUCT_ID','MONTH'],validate='many_to_one')
inv['INVENTORY_VALUE']=inv.STOCK_QUANTITY*inv.UNIT_COST
avg=inv[inv.MONTH.str.startswith('2025')].groupby(['PRODUCT_ID','REGION']).INVENTORY_VALUE.mean().rename('AVG_INVENTORY_VALUE')
annual=monthly[monthly.MONTH.str.startswith('2025')].groupby(['PRODUCT_ID','REGION']).COGS.sum().rename('ANNUAL_COGS')
turn=pd.concat([avg,annual],axis=1).reset_index(); turn['INVENTORY_TURNOVER']=turn.ANNUAL_COGS/turn.AVG_INVENTORY_VALUE
turn.to_csv(OUT/'INVENTORY_TURNOVER.csv',index=False); stock.to_csv(OUT/'STOCK_POSITION.csv',index=False)
summary={'revenue_gbp':round(sales.REVENUE.sum(),2),'gross_profit_gbp':round(sales.GROSS_PROFIT.sum(),2),'margin_pct':float(sales.GROSS_PROFIT.sum()/sales.REVENUE.sum()),'orders':int(sales.ORDER_ID.nunique()),'aov_gbp':float(sales.REVENUE.sum()/sales.ORDER_ID.nunique()),'checks_failure_counts':checks,'synthetic':True}
(REPORT/'validation.json').write_text(json.dumps(summary,indent=2))
agg=metrics.groupby('MODEL')[['TEST_MAE','TEST_RMSE']].mean()
selected=metrics[metrics.SELECTED==1].TEST_MAE.mean()
profit=sales.groupby('PRODUCT_NAME').agg(REVENUE=('REVENUE','sum'),PROFIT=('GROSS_PROFIT','sum')).sort_values('PROFIT',ascending=False)
profit.to_csv(REPORT/'product_profitability.csv')
report=f'''# Business findings — synthetic demonstration\n\nRevenue: £{summary['revenue_gbp']:,.2f}; gross profit: £{summary['gross_profit_gbp']:,.2f}; weighted margin: {summary['margin_pct']:.1%}.\n\nHighest total product profit: {profit.index[0]}.\n\nMean per-series test MAE for validation-selected models: {selected:.2f} units.\n\n{agg.to_markdown() if False else agg.to_string()}\n\n{int((stock.RISK=='Potential shortage').sum())} product/region pairs have December stock below January predicted demand. Review replenishment and lead times before buying.\n\nLaptop cost inflation and promotional discounts were deliberately injected from July 2025: investigate discount policy and supplier terms. These are known simulation mechanisms, not causal discoveries from real business evidence.\n\nInventory flags ignore incoming purchases, lead times, safety stock, backorders and service-level targets. Forecasts estimate observed sales, not unconstrained demand. No confidence intervals or production deployment are claimed.\n'''
(REPORT/'BUSINESS_FINDINGS.md').write_text(report)
fig,axes=plt.subplots(2,2,figsize=(13,8)); fig.suptitle('Enterprise Intelligence | Synthetic demonstration | GBP')
mt=monthly.groupby('MONTH')[['REVENUE','GROSS_PROFIT']].sum(); mt.index=pd.to_datetime(mt.index); mt.plot(ax=axes[0,0],title='Sales and gross profit'); axes[0,0].tick_params(axis='x',rotation=30)
profit.PROFIT.plot.bar(ax=axes[0,1],title='Product gross profit',rot=45)
ff=f[(f.PRODUCT_ID=='P002')&(f.REGION=='North')]; gg=monthly[(monthly.PRODUCT_ID=='P002')&(monthly.REGION=='North')]
axes[1,0].plot(pd.to_datetime(gg.MONTH),gg.QUANTITY,label='Actual'); axes[1,0].plot(pd.to_datetime(ff.MONTH),ff.FORECAST_QUANTITY,label='Forecast'); axes[1,0].legend(); axes[1,0].set_title('Monitor / North demand')
stock.groupby('RISK').size().plot.bar(ax=axes[1,1],title='Stock pressure pairs',rot=15)
fig.autofmt_xdate(rotation=30); fig.tight_layout(); fig.savefig(REPORT/'dashboard_preview.png',dpi=150); plt.close(fig)
con.close(); print(json.dumps(summary,indent=2)); print('Pipeline complete: outputs/ and data/processed/')
