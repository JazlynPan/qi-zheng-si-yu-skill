#!/usr/bin/env python3
"""執行：檢查人工分卡候選是否漏掉指定正文區間；不判斷概念或原書題數。"""
import argparse,json,re,bisect
from pathlib import Path
from source_spans import Source

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
 p.add_argument('--batch',type=Path,action='append',required=True);p.add_argument('--start',required=True);p.add_argument('--end',required=True)
 p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
 s=Source(a.source);q,_,_=s.extract(a.start,a.end,first=a.first,last=a.last);left=s.text.index(a.start,s.offsets[a.first-1]);mask=bytearray(len(q));records=[];missing=[]
 for batch in a.batch:records.extend(json.loads(batch.read_text()))
 for r in records:
  for v in r['fields'].values():
   if v in ['原文未提及','无','無','原文以圖表呈現']:continue
   for block in re.split(r'\n\s*\n',v):
    if not block:continue
    at=q.find(block)
    if at<0:missing.append({'卡名':r['name'],'片段':block[:80]});continue
    mask[at:at+len(block)]=b'\1'*len(block)
 gaps=[];i=0
 while i<len(q):
  if mask[i]:i+=1;continue
  j=i+1
  while j<len(q)and not mask[j]:j+=1
  gaps.append({'起頁':bisect.bisect_right(s.offsets,left+i),'迄頁':bisect.bisect_right(s.offsets,left+j-1),'原文':q[i:j]});i=j
 report={'候選卡數':len(records),'正文區間字元數':len(q),'已覆蓋字元數':sum(mask),'未覆蓋片段數':len(gaps),'未覆蓋片段':gaps,'候選未對應片段':missing,'限制':'只核對已抽取文字與候選引文的連續覆蓋，不驗證抽取器是否漏字，也不判斷一段是否應另立一題。'}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in ['未覆蓋片段','候選未對應片段']},ensure_ascii=False))
if __name__=='__main__':main()
