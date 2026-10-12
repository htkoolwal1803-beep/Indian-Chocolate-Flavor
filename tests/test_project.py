import json,sqlite3,unittest
from pathlib import Path
import pandas as pd
from src.features import weight,flavors,canonical,format_type
from src.import_capture import parse
ROOT=Path(__file__).resolve().parents[1]

class ProjectTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=sqlite3.connect(ROOT/'data/chocolate.sqlite')
 @classmethod
 def tearDownClass(cls):cls.c.close()
 def test_integrity(self):
  self.assertEqual(self.c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
  self.assertEqual(self.c.execute('PRAGMA foreign_key_check').fetchall(),[])
 def test_multipack_prefix(self):self.assertEqual(weight('3x51 g - (Multipack)'),153)
 def test_pack_of(self):self.assertEqual(weight('16 g - (Pack of 9)'),144)
 def test_set_of(self):self.assertEqual(weight('50 g - (Set of 3)'),150)
 def test_total_not_double_counted(self):
  self.assertEqual(weight('111 g - (15x7.4 g)'),111)
  self.assertEqual(weight('264 g - (24 pcs x 11 g each)'),264)
 def test_missing_weight(self):self.assertIsNone(weight(None))
 def test_named_flavors(self):
  self.assertEqual(set(flavors('Fruit N Nut Dark Chocolate')),{'fruit','nuts'})
  self.assertEqual(flavors('Milk Chocolate'),'no_named_inclusion'.split())
 def test_duplicate_alias(self):
  self.assertEqual(canonical('Cadbury Dairy Milk Silk Oreo Red Velvet Chocolate Bar'),canonical('Cadbury Dairy Milk Silk Dairy Milk Silk Chocolate Bar - Oreo Red Velvet'))
 def test_format_precedence(self):
  self.assertEqual(format_type('KitKat Assorted Gift Pack'),'gift_assortment')
  self.assertEqual(format_type('KitKat Caramel Wafer'),'wafer')
 def test_prices(self):
  for p,g,u in self.c.execute('SELECT price_inr,total_weight_g,price_per_100g FROM priced_products'):self.assertAlmostEqual(p/g*100,u)
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM products WHERE reference_price_inr<price_inr').fetchone()[0],0)
 def test_missing_price_excluded_from_model(self):
  self.assertGreater(self.c.execute('SELECT COUNT(*) FROM products WHERE price_inr IS NULL').fetchone()[0],0)
  self.assertEqual(self.c.execute('SELECT COUNT(*) FROM priced_products WHERE price_inr IS NULL').fetchone()[0],0)
 def test_snapshot_audit(self):
  raw=json.loads((ROOT/'data/observations.json').read_text(encoding='utf-8'))
  n=self.c.execute('SELECT COUNT(*) FROM products').fetchone()[0]+self.c.execute('SELECT COUNT(*) FROM exclusions').fetchone()[0]
  self.assertEqual(n,len(raw))
 def test_sources(self):
  urls={s['url'] for s in json.loads((ROOT/'data/sources.json').read_text())}
  self.assertTrue(all(x[0] in urls for x in self.c.execute('SELECT source_url FROM products')))
 def test_grouped_split(self):
  d=pd.read_csv(ROOT/'reports/tables/predictions_family_grouped.csv')
  self.assertTrue((d.groupby('family_group').fold.nunique()==1).all())
 def test_brand_split(self):
  d=pd.read_csv(ROOT/'reports/tables/predictions_unseen_brand.csv')
  self.assertTrue((d.groupby('brand').fold.nunique()==1).all())
 def test_mainstream_scope(self):
  self.assertEqual({x[0] for x in self.c.execute('SELECT DISTINCT brand FROM products')},{'Cadbury','Amul','Nestle',"Hershey's",'Ferrero Rocher','Snickers'})
 def test_inline_line_markers(self):
  text='L70: ### Amul Dark Chocolate L71: 4.2 15803 Ratings\nL73: 150 g\nL75: ₹180.00'
  row=parse(text,{'source_id':'test','brand':'Amul','url':'https://example.com'})[0]
  self.assertEqual(row['title'],'Amul Dark Chocolate');self.assertEqual(row['rating_count'],15803)
 def test_next_card_discount_not_reference_price(self):
  text='### Amul Dark Chocolate\n150 g\n₹180.00\n  * ₹43 OFF\n### Amul Orange\n150 g\n₹180.00'
  row=parse(text,{'source_id':'test','brand':'Amul','url':'https://example.com'})[0]
  self.assertIsNone(row['reference_price_inr'])
 def test_matched_amul_comparison(self):
  d=pd.read_csv(ROOT/'reports/tables/amul_matched_comparison.csv')
  self.assertEqual(len(d),3);self.assertTrue((d.total_weight_g==150).all());self.assertTrue((d.price_inr==180).all())

if __name__=='__main__':unittest.main()
