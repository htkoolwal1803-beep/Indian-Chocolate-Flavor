import json,re,sqlite3
from pathlib import Path
import pandas as pd
from .features import weight,flavors,format_type,subbrand,canonical,family
ROOT=Path(__file__).resolve().parents[1]

def build():
 db=ROOT/'data/chocolate.sqlite'
 if db.exists():db.unlink()
 c=sqlite3.connect(db);c.executescript((ROOT/'sql/schema.sql').read_text())
 sources=json.loads((ROOT/'data/sources.json').read_text())
 for s in sources:
  c.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?)',tuple(s[k] for k in ['source_id','url','brand','retrieved_date','crawl_age_days_approx','method','location']))
 observations=json.loads((ROOT/'data/observations.json').read_text(encoding='utf-8'));seen=set()
 for p in observations:
  key=(p['brand'],canonical(p['title']),weight(p['pack_label']))
  reason=None
  if p['pack_label'] is None and p['price_inr'] is None:reason='incomplete search preview without a product card'
  elif re.search('compound|slab|polo mint',p['title'],re.I):reason='baking ingredient or non-chocolate candy'
  elif key in seen:reason='duplicate normalized title and total pack weight; first observed row retained'
  if reason:
   c.execute('INSERT INTO exclusions VALUES (?,?,?)',(p['observation_id'],p['title'],reason));continue
  seen.add(key)
  cocoa=re.search(r'(\d+(?:\.\d+)?)\s*%',p['title'])
  c.execute('INSERT INTO products VALUES ('+','.join('?' for _ in range(16))+')',(
   p['observation_id'],p['source_id'],p['brand'],p['title'],p['pack_label'],weight(p['pack_label']),
   p['price_inr'],p['reference_price_inr'],p['rating'],p['rating_count'],int(p['notify_me']),
   format_type(p['title']),subbrand(p['title'],p['brand']),float(cocoa[1]) if cocoa else None,
   family(p['title'],p['brand']),p['source_url']))
  c.executemany('INSERT INTO product_flavors VALUES (?,?)',[(p['observation_id'],f) for f in flavors(p['title'])])
 c.commit();assert not c.execute('PRAGMA foreign_key_check').fetchall()
 out=ROOT/'reports/tables';out.mkdir(parents=True,exist_ok=True)
 for q in sorted((ROOT/'sql').glob('[0-9]*.sql')):pd.read_sql_query(q.read_text(),c).to_csv(out/(q.stem+'.csv'),index=False)
 pd.read_sql_query('SELECT * FROM priced_products',c).to_csv(ROOT/'data/analysis_products.csv',index=False)
 pd.read_sql_query('SELECT * FROM exclusions',c).to_csv(out/'exclusions.csv',index=False)
 print('Products:',c.execute('SELECT COUNT(*) FROM products').fetchone()[0],'; priced:',c.execute('SELECT COUNT(*) FROM priced_products').fetchone()[0])
 c.close()

if __name__=='__main__':build()
