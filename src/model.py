import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer,TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error,r2_score
from sklearn.model_selection import GroupKFold,LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from .features import FLAVORS,flavors
ROOT=Path(__file__).resolve().parents[1]

def estimator(full):
 cats=['brand','format']
 transforms=[('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cats)]
 if full:
  numeric=['total_weight_g','cocoa_pct']+list(FLAVORS)
  transforms.append(('numeric',Pipeline([('impute',SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True)),('scale',StandardScaler())]),numeric))
 return TransformedTargetRegressor(regressor=Pipeline([('features',ColumnTransformer(transforms)),('model',Ridge(alpha=10))]),func=np.log,inverse_func=np.exp)

def evaluate(d,label,group_col,splitter):
 d=d.reset_index(drop=True); y=d.price_per_100g.to_numpy();groups=d[group_col]
 preds={name:np.zeros(len(d)) for name in ['global_median','brand_format_median','brand_format_ridge','full_ridge']};folds=np.zeros(len(d),int)
 for fold,(train,test) in enumerate(splitter.split(d,y,groups)):
  assert not set(groups.iloc[train]) & set(groups.iloc[test])
  tr,te=d.iloc[train],d.iloc[test];global_median=np.median(y[train])
  preds['global_median'][test]=global_median
  bybrand=tr.groupby('brand').price_per_100g.median().to_dict()
  byformat=tr.groupby(['brand','format']).price_per_100g.median().to_dict()
  preds['brand_format_median'][test]=[byformat.get((r.brand,r.format),bybrand.get(r.brand,global_median)) for r in te.itertuples()]
  for name,full in [('brand_format_ridge',False),('full_ridge',True)]:
   model=estimator(full);model.fit(tr,y[train]);preds[name][test]=model.predict(te)
  folds[test]=fold
 metrics=[dict(validation=label,model=k,n=len(d),groups=groups.nunique(),mae=mean_absolute_error(y,v),r2=r2_score(y,v)) for k,v in preds.items()]
 p=d[['observation_id','brand','title','family_group','price_per_100g']].copy();p['fold']=folds
 for k,v in preds.items():p[k]=v
 p.to_csv(ROOT/f'reports/tables/predictions_{label}.csv',index=False)
 delta=np.abs(y-preds['brand_format_median'])-np.abs(y-preds['full_ridge'])
 g=pd.DataFrame({'group':groups.to_numpy(),'delta':delta}).groupby('group').delta.agg(['sum','count'])
 rng=np.random.default_rng(42);idx=rng.integers(0,len(g),size=(2000,len(g)))
 draws=g['sum'].to_numpy()[idx].sum(axis=1)/g['count'].to_numpy()[idx].sum(axis=1)
 return metrics,dict(validation=label,mae_improvement_full_vs_baseline=float(delta.mean()),
  lower95=float(np.quantile(draws,.025)),upper95=float(np.quantile(draws,.975)))

def run():
 d=pd.read_csv(ROOT/'data/analysis_products.csv')
 for f in FLAVORS:d[f]=d.title.map(lambda t:int(f in flavors(t)))
 scenarios=[('family_grouped',d,'family_group',GroupKFold(5)),
  ('unseen_brand',d,'brand',LeaveOneGroupOut()),
  ('recent_sources',d[d.crawl_age_days_approx<=30],'family_group',GroupKFold(5)),
  ('exclude_gifts',d[d['format']!='gift_assortment'],'family_group',GroupKFold(5))]
 metrics=[];intervals=[]
 for label,subset,group,split in scenarios:
  m,i=evaluate(subset,label,group,split);metrics+=m;intervals.append(i)
 pd.DataFrame(metrics).to_csv(ROOT/'reports/tables/model_metrics.csv',index=False)
 (ROOT/'reports/model_uncertainty.json').write_text(json.dumps(intervals,indent=2))
 print(pd.DataFrame(metrics).to_string(index=False))

if __name__=='__main__':run()
