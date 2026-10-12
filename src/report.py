import json,sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
COLORS=['#af6036','#775898','#ae862a','#54352e','#258b83','#a44950']

def save(fig,name):
 fig.savefig(ROOT/f'reports/figures/{name}.png',dpi=150,bbox_inches='tight',facecolor=fig.get_facecolor());plt.close(fig)

def run():
 (ROOT/'reports/figures').mkdir(parents=True,exist_ok=True)
 plt.rcParams.update({'figure.facecolor':'#faf7f2','axes.facecolor':'#faf7f2','axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':15,'axes.titleweight':'bold'})
 conn=sqlite3.connect(ROOT/'data/chocolate.sqlite');allp=pd.read_sql_query('SELECT * FROM products',conn);d=pd.read_sql_query('SELECT * FROM priced_products',conn)
 brands=sorted(d.brand.unique());palette=dict(zip(brands,COLORS))
 med=d.groupby('brand').agg(priced_listings=('observation_id','size'),median_inr_per_100g=('price_per_100g','median'),min_price=('price_per_100g','min'),max_price=('price_per_100g','max'))
 med.to_csv(ROOT/'reports/tables/brand_medians.csv')
 fig,ax=plt.subplots(figsize=(10,5.5));rng=np.random.default_rng(42)
 for i,b in enumerate(brands):
  g=d[d.brand==b];ax.scatter(g.price_per_100g,i+rng.uniform(-.15,.15,len(g)),color=palette[b],s=35,alpha=.65)
  ax.plot([g.price_per_100g.median()]*2,[i-.25,i+.25],color='#222222',lw=3)
 ax.set_yticks(range(len(brands)),[f'{b} (n={len(d[d.brand==b])})' for b in brands]);ax.set_xlabel('Indexed listed INR per 100g');ax.grid(axis='x',alpha=.15)
 ax.set_title('Mainstream chocolate price positioning in Indian retail',loc='left',pad=20)
 fig.text(.13,-.06,'Retailer-index snapshots with different crawl dates; delivery location unspecified.\nDots = listings; black lines = medians. Product formats and pack sizes vary.',fontsize=9,color='#555')
 save(fig,'price_positioning')
 f=pd.read_sql_query('SELECT p.brand,f.flavor,COUNT(*) n FROM product_flavors f JOIN products p USING(observation_id) GROUP BY 1,2',conn)
 pivot=f.pivot(index='flavor',columns='brand',values='n').fillna(0).astype(int)
 fig,ax=plt.subplots(figsize=(11,5.5));ax.imshow(pivot,cmap='YlOrBr',aspect='auto')
 ax.set_xticks(range(len(brands)),pivot.columns,rotation=20,ha='right');ax.set_yticks(range(len(pivot)),[x.replace('_',' ') for x in pivot.index])
 for i in range(len(pivot)):
  for j in range(len(brands)):ax.text(j,i,str(pivot.iloc[i,j]),ha='center',va='center',color='white' if pivot.iloc[i,j]>20 else '#222')
 ax.set_title('Named flavor families across sampled mainstream brands',loc='left',pad=18)
 fig.text(.13,-.12,'Title-based multi-label tags; pack variants can repeat a flavor. Counts reflect observed\nlistings, not unique recipes, popularity or market share.',fontsize=9,color='#555');save(fig,'flavor_assortment')
 ratings=allp[allp.rating_count.notna()].copy()
 fig,ax=plt.subplots(figsize=(10,5))
 for b,g in ratings.groupby('brand'):ax.scatter(g.rating_count,g.rating,color=palette[b],label=b,alpha=.6,s=35)
 ax.set_xscale('log');ax.set_xlabel('Displayed rating count (log scale)');ax.set_ylabel('Displayed average stars');ax.set_title('Rating volume matters when interpreting high scores',loc='left',pad=18);ax.legend(ncol=3,fontsize=8,loc='lower right');ax.grid(alpha=.15)
 fig.text(.13,-.11,'Ratings may be pooled across packs. Counts are not sales or unique consumers.\nOnly displayed aggregates were captured; no individual review text is available.',fontsize=9,color='#555');save(fig,'rating_evidence')
 metrics=pd.read_csv(ROOT/'reports/tables/model_metrics.csv');m=metrics[metrics.validation=='family_grouped']
 fig,ax=plt.subplots(figsize=(10,4.5));ax.barh(m.model.str.replace('_',' '),m.mae,color=['#b9aea2','#258b83','#ad8c70','#54352e'])
 for i,v in enumerate(m.mae):ax.text(v+.8,i,f'{v:.1f}',va='center')
 ax.set_xlim(0,m.mae.max()*1.2);ax.set_xlabel('Out-of-fold MAE, INR per 100g (lower is better)');ax.set_title('Price models compared with simple baselines',loc='left',pad=18)
 fig.text(.13,-.11,'Five folds grouped by brand, subbrand, format and flavor-family combination.\nExploratory prediction on indexed observations; not a live market forecast.',fontsize=9,color='#555');save(fig,'model_validation')
 sensitivity=[]
 for b,g in ratings.groupby('brand'):
  prior=g.rating.mean()
  for strength in [20,100,500]:
   a=g[['observation_id','brand','title','rating','rating_count']].copy();a['prior_strength']=strength
   a['score']=(g.rating*g.rating_count+strength*prior)/(g.rating_count+strength);a['rank']=a.score.rank(method='min',ascending=False);sensitivity.append(a)
 pd.concat(sensitivity).to_csv(ROOT/'reports/tables/rating_sensitivity.csv',index=False)
 # Explicit matched comparison within one source and equal pack mass.
 amul=d[(d.brand=='Amul') & d.title.isin(['Amul Dark Chocolate','Amul Tropical Orange Dark Chocolate','Amul Fruit N Nut, Dark Chocolate- 55% Rich In Cocoa'])]
 amul[['title','total_weight_g','price_inr','price_per_100g']].to_csv(ROOT/'reports/tables/amul_matched_comparison.csv',index=False)
 recent=d[d.crawl_age_days_approx<=30].groupby('brand').price_per_100g.median();recent.to_csv(ROOT/'reports/tables/recent_source_medians.csv')
 flavor=pd.read_csv(ROOT/'reports/tables/02_flavor_assortment.csv');baseline=m.set_index('model').loc['brand_format_median','mae'];full=m.set_index('model').loc['full_ridge','mae']
 lines=['# Findings: mainstream chocolates sold in India','',f'**{len(allp)} retained retail listings; {len(d)} priced listings; six mainstream brands; {len(ratings)} listings with aggregate ratings.**',
 '', 'Sources were retrieved on 12 October 2026 from public retailer-index extracts. Their displayed crawl ages range from today to approximately three months; prices are not a synchronized live snapshot. The delivery location is unspecified. All comparisons are descriptive and specific to this sample.',
 '', '## 1. An equal-pack flavor comparison: Amul','',
 'The sampled 150g Amul Dark Chocolate, Tropical Orange and Fruit N Nut cards each list INR 180 (INR 120/100g). In this matched example, those named inclusions do not carry a listed-price premium. This does not establish equal production cost, equal willingness to pay or unchanged prices elsewhere.',
 '', '## 2. Separate brand, format and pack size','', '| Brand | Priced listings | Median INR/100g |','|---|---:|---:|']
 for b,r in med.iterrows():lines.append(f'| {b} | {int(r.priced_listings)} | {r.median_inr_per_100g:.2f} |')
 lines+=['','![Price positioning](figures/price_positioning.png)','',
 'These medians mix formats and include assorted/gift packs. `03_brand_format_flavors.csv` compares flavors within brand and format; the model also controls for format. A separate evaluation excludes gift/assortment listings.',
 '', '## 3. Flavor breadth is not demand','']
 for r in flavor.itertuples():
  if r.flavor!='no_named_inclusion':lines.append(f'- {r.flavor.replace("_"," ")}: {r.listings} listings ({r.pct_listings:.1f}%).')
 lines+=['','![Flavor assortment](figures/flavor_assortment.png)','',
 'Tags overlap and are derived from marketed titles. A flavor absent from a title can still be present in the ingredients. Multiple sizes can repeat a recipe. No national flavor popularity, sales share or market gap is inferred.',
 '', '## 4. Customer rating evidence needs context','',
 f'{int((ratings.rating_count<100).sum())} of {len(ratings)} rated listings have fewer than 100 displayed ratings. '
 'The within-brand shrinkage table reduces the influence of tiny counts, with pseudo-count sensitivity at 20, 100 and 500. '
 'Counts may be shared across pack variants, so they are never summed as unique reviews or consumers. There are no individual reviews in this revised dataset; no sentiment or taste-versus-delivery claim is made.',
 '', '![Ratings](figures/rating_evidence.png)','',
 '## 5. Out-of-fold model comparison','',f'Principal grouped MAE: **INR {baseline:.2f}/100g** for the brand/format median baseline and **INR {full:.2f}/100g** for full ridge regression.',
 '', '![Model comparison](figures/model_validation.png)','',
 'The full model uses brand, format, pack mass, explicitly named cocoa percentage and flavor flags. Preprocessing is fit inside training folds. Related products stay in the same family group. Missing prices are never imputed into the target. The model uses fixed alpha=10, with no hyperparameter selection on test results.',
 'See `model_metrics.csv` for leave-one-brand-out transfer, recent-source-only (approximate crawl age at most 30 days) and no-gift sensitivity results. Source recency and brand are confounded: excluding older pages drops Ferrero and Cadbury Silk. Bootstrap intervals resample fixed held-out errors by group; they are descriptive, not causal.',
 '', '## Business actions supported by this evidence','',
 '- Benchmark same-weight and same-format products before interpreting flavor price differences.',
 '- Use low-count ratings as research prompts; commission a representative consumer preference study before selecting a launch flavor.',
 '- Validate candidate price comparisons against one delivery postcode and one collection date before a pricing decision.',
 '- Expand to other retailers and actual sales outcomes before forecasting demand.',
 '', '## Traceability','',
 'Every record in `data/observations.json` carries a source URL, source ID, original pack label and source-card position. `data/sources.json` records retrieval method and approximate crawl age. Seven SQL analyses, a model card, data dictionary, executed notebook and tests accompany this report.']
 (ROOT/'reports/FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 (ROOT/'reports/RESUME_BULLETS.md').write_text(f'''# Resume bullets

- Built a reproducible SQL/Python analysis of {len(allp)} retail chocolate listings across Cadbury, Amul, Nestle, Hershey's, Ferrero Rocher and Snickers, with normalized pack pricing, source provenance and seven analytical SQL queries.
- Compared ridge regression with median baselines using grouped and unseen-brand validation, cluster-bootstrap error analysis and source-recency/product-format sensitivity checks.
- Analyzed flavor assortment and aggregate customer ratings with transparent feature rules and within-brand shrinkage, documenting pooled-rating and retailer-sampling limitations.

Use only after reviewing and understanding the notebook. Do not claim sales impact, representative national coverage or a trained sentiment model.
''',encoding='utf-8')
 conn.close()

if __name__=='__main__':run()
