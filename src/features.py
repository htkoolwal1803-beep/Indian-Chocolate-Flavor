import re
import unicodedata

FLAVORS={
 'nuts':r'almond|hazelnut|peanut|pistach|\bpista\b|walnut|\bnuts?\b|nutty',
 'fruit':r'cranberr|raisin|strawberr|blueberr|raspberr|\bberry\b|mango|pineapple|orange|pomegranate|\bfruit\b|\bplum\b|acai|goji|guava|limon',
 'coffee':r'coffee|mocha|espresso',
 'caramel_butterscotch':r'caramel|butterscotch|toffee',
 'cookie_brownie':r'oreo|cookies?|brownie|cake',
 'salt':r'\bsalt(?:ed)?\b',
 'spice_tea':r'chili|chilli|kesar|green.?t\b|green tea',
 'dessert_specialty':r'kunafa|kulfi|rabdi|bubblegum',
}

def flavors(title):
 t=''.join(c for c in unicodedata.normalize('NFKD',title.lower()) if not unicodedata.combining(c))
 return [k for k,v in FLAVORS.items() if re.search(v,t)] or ['no_named_inclusion']

def weight(label):
 """Parse total pack grams; parentheses can specify count OR repeat total detail."""
 if not label:return None
 m=re.match(r'(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*g\b',label,re.I)
 if m:return float(m[1])*float(m[2])
 m=re.match(r'(\d+(?:\.\d+)?)\s*g\b',label,re.I)
 if not m:return None
 total=float(m[1]); count=re.search(r'(?:pack|set)\s+of\s+(\d+)',label,re.I)
 return total*int(count[1]) if count else total

def format_type(title):
 t=title.lower()
 if re.search('gift|assorted|variety pack|festive|pralines|collection',t):return 'gift_assortment'
 if re.search('wafer|kitkat|munch|crispello',t):return 'wafer'
 if re.search('kisses|minis|miniatures|mini treats|balls|bites|chocominis|almondo|moments|home treat|tubes|truffles',t):return 'bites_tubes'
 if 'snickers' in t or 'bar one' in t:return 'filled_bar'
 return 'bar_other'

def subbrand(title,brand):
 t=title.lower()
 for name in ['silk','kitkat','munch','milkybar','kisses','exotic','moments','bar one']:
  if name in t:return name
 return brand.lower()

def canonical(title):
 t=title.lower().replace('roasted','roast')
 for phrase in ['cadbury dairy milk silk','cadbury dairy milk','dairy milk silk','dairy milk']:
  t=re.sub(r'('+re.escape(phrase)+r')\s+\1',r'\1',t)
 t=re.sub(r'[^a-z0-9]+',' ',t)
 t=t.strip().replace('chocolate bars','chocolate bar')
 if 'silk' in t and 'oreo red velvet' in t:return 'cadbury dairy milk silk oreo red velvet chocolate bar'
 return t

def family(title,brand):
 # Conservative grouping: related types of flavored products cannot cross folds.
 return '|'.join([brand,subbrand(title,brand),format_type(title),'+'.join(flavors(title))])
