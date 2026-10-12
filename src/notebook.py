from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]

def run():
 md=nbf.v4.new_markdown_cell;code=nbf.v4.new_code_cell
 cells=[md('''# Chocolate Flavor Intelligence: mainstream brands in India

**Cadbury · Amul · Nestle · Hershey's · Ferrero Rocher · Snickers**

Analyze flavor assortment, normalized retail pricing and customer rating evidence using real public retailer-index observations. This is not national market share or a live synchronized price panel. Read the [data dictionary](../docs/DATA_DICTIONARY.md) for capture dates and limitations.'''),
 code('''from pathlib import Path
import os, sys, sqlite3, json
import pandas as pd
from IPython.display import display, Image
ROOT=Path.cwd()
if ROOT.name == 'notebooks': ROOT=ROOT.parent
os.chdir(ROOT)
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from src.run import main
main()
conn=sqlite3.connect('data/chocolate.sqlite')'''),
 md('''## 1. Inspect provenance and scope

Retrieval date differs from crawl age. Seven category pages cover six brand groups. Raw records remain available alongside exclusions. Product-card IDs are snapshot-specific and are not stable manufacturer SKUs.'''),
 code('''display(pd.read_csv('reports/tables/07_source_quality.csv'))
display(pd.read_csv('reports/tables/exclusions.csv'))
display(pd.read_sql_query("SELECT brand,COUNT(*) AS listings,COUNT(rating) AS rated FROM products GROUP BY brand",conn))'''),
 md('''## 2. Pack normalization changes the comparison

`3x51g` means 153g total; `111g (15x7.4g)` already states total mass. Price comparisons use total grams, not one unit's mass. The SQL view excludes missing prices without inventing targets. Formats such as wafers and gift packs are explicitly separated.'''),
 code('''from src.features import weight
display(pd.DataFrame({'pack':['3x51 g - (Multipack)','16 g - (Pack of 9)','111 g - (15x7.4 g)'],
                      'total_g':[weight(x) for x in ['3x51 g - (Multipack)','16 g - (Pack of 9)','111 g - (15x7.4 g)']]}))
display(pd.read_csv('reports/tables/brand_medians.csv'))
display(pd.read_csv('reports/tables/amul_matched_comparison.csv'))
display(Image(filename='reports/figures/price_positioning.png'))'''),
 md('''## 3. SQL and interpretable flavor features

Tags describe marketed title cues, not a full ingredient inventory. Categories overlap. Listings can repeat recipes in multiple pack sizes; observed counts are not popularity or demand. The query below compares a flavor with its own brand-format benchmark, which helps expose confounding but does not establish causality.'''),
 code('''query=Path('sql/03_brand_format_flavors.sql').read_text()
print(query)
display(pd.read_sql_query(query,conn).head(20))
display(Image(filename='reports/figures/flavor_assortment.png'))'''),
 md('''## 4. Consumer evidence: aggregate ratings

Only displayed average stars and counts were captured. Ratings may be pooled across packs, so counts are not summed as unique reviews. No individual review text or sentiment analysis is claimed.

Descriptive shrinkage uses an equal-weight brand mean as prior and pseudo-counts 20/100/500. This is not a calibrated posterior or a population preference estimate. A high average supported by very few ratings is a question for further research.'''),
 code('''display(pd.read_csv('reports/tables/06_rating_evidence.csv'))
display(pd.read_csv('reports/tables/04_rating_shrinkage.csv').groupby('brand',sort=False).head(2))
display(Image(filename='reports/figures/rating_evidence.png'))'''),
 md('''## 5. Predictive experiment and sensitivity

The target is listed INR/100g. Compare global and brand/format median baselines with ridge models. The full model adds mass, sparse cocoa percentage and flavor flags. Encoding, imputation and scaling fit inside each training fold; alpha=10 is fixed without tuning on test predictions.

Family groups combine brand, subbrand, format and flavor tags. Similar packs stay together. Leave-one-brand-out measures transfer. Recent-source-only and no-gift evaluations expose sensitivity to source age and merchandising mix. Cluster-bootstrap intervals resample fixed held-out errors, not the entire fitting procedure.'''),
 code('''display(pd.read_csv('reports/tables/model_metrics.csv'))
display(pd.DataFrame(json.loads(Path('reports/model_uncertainty.json').read_text())))
display(Image(filename='reports/figures/model_validation.png'))'''),
 md('''## 6. Business interpretation

The sampled 150g Amul plain dark, orange and fruit-and-nut products share a listed INR180 price. This is a useful matched comparison, not a national pricing rule. Brand and format structure matter; a richer model must earn its complexity against baselines.

Before a pricing or product-launch decision, collect synchronized prices for one postcode, add other retailers, verify ingredients and obtain independent consumer/sales outcomes. Read [the generated findings](../reports/FINDINGS.md) and [model card](../docs/MODEL_CARD.md).

**Exercises:** exclude listings with Notify Me; compare medians within format; audit source-age effects; change one flavor rule and review affected records. Treat exploratory model changes as sensitivity tests rather than selecting the best reported test score.'''),
 code("conn.close()\nprint('Offline analysis completed; reports and SQL tables are regenerated.')")]
 nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
 path=ROOT/'notebooks/01_chocolate_intelligence.ipynb';path.parent.mkdir(exist_ok=True)
 NotebookClient(nb,timeout=300,startup_timeout=60,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
 nbf.write(nb,path);print('Executed',path.name)
if __name__=='__main__':run()
