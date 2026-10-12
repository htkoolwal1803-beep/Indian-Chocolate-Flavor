"""Parse saved public retailer text extracts into a candidate factual snapshot.

python -m src.import_capture --captures path/to/text --out data/candidate.json
Files must be named <source_id>.txt and correspond to data/sources.json.
This performs no network requests and does not silently overwrite the snapshot.
"""
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def parse(text,source):
 text=re.sub(r'L\d+:\s?','\n',text)
 text=re.sub(r'\ue200cite\ue202\d+†([^\ue201]+)\ue201',r'\1',text)
 matches=list(re.finditer(r'### (.+)',text));rows=[]
 for i,m in enumerate(matches):
  title=m[1].strip()
  if not title.lower().startswith(('amul','nestle','cadbury','ferrero','snickers','hershey')):continue
  chunk=text[m.end():matches[i+1].start() if i+1<len(matches) else len(text)]
  chunk=chunk.split('\n# ')[0].split('\n## ')[0]
  rating=re.search(r'\b([1-5](?:\.\d+)?)\s+([\d,]+)\s+Ratings?\b',chunk)
  pack=re.search(r'(?m)^\s*((?:\d+(?:\.\d+)?\s*[x×]\s*)?\d+(?:\.\d+)?\s*g\b[^\n]*)',chunk)
  line=next((s.strip() for s in chunk.splitlines() if re.fullmatch(r'\s*₹[\d,.]+(?:\s*₹[\d,.]+)?\s*',s)),'')
  prices=re.findall(r'₹\s*([\d,]+(?:\.\d+)?)',line)
  rows.append(dict(observation_id=source['source_id']+'_'+str(i+1).zfill(3),source_id=source['source_id'],brand=source['brand'],title=title,
   pack_label=pack[1].strip() if pack else None,price_inr=float(prices[0].replace(',','')) if prices else None,
   reference_price_inr=float(prices[1].replace(',','')) if len(prices)>1 else None,
   rating=float(rating[1]) if rating else None,rating_count=int(rating[2].replace(',','')) if rating else None,
   notify_me='Notify Me' in chunk,source_url=source['url'],source_position=i+1))
 return rows

def main():
 a=argparse.ArgumentParser();a.add_argument('--captures',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args()
 if args.out.resolve()==(ROOT/'data/observations.json').resolve():raise ValueError('Write a candidate file and review it before replacing observations.json')
 rows=[]
 for s in json.loads((ROOT/'data/sources.json').read_text()):
  text=(args.captures/(s['source_id']+'.txt')).read_text(encoding='utf-8');parsed=parse(text,s)
  if not parsed:raise ValueError('No product cards found for '+s['source_id'])
  rows+=parsed
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 print(len(rows),'candidate rows. Review fields and update source retrieval/crawl metadata before adoption.')
if __name__=='__main__':main()
