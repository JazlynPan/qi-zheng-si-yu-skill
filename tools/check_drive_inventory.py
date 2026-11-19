#!/usr/bin/env python3
"""執行：比對已取得的雲端清單與帳本；不下載、不改帳本、不宣稱驗證遠端雜湊。"""
import argparse,json,re,hashlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--ledger',type=Path,default=Path('docs/來源清單.md'))
 p.add_argument('--report',type=Path,required=True);p.add_argument('--local-manifest',type=Path,action='append',default=[])
 a=p.parse_args();files=json.loads(a.snapshot.read_text());files=files['檔案']if isinstance(files,dict)else files;remote={r['id']:r for r in files};ledger={};local={}
 for line in a.ledger.read_text().splitlines():
  if not line.startswith('|') or 'https://'not in line:continue
  c=line.strip('|').split('|');m=re.search(r'/(?:d|folders)/([^/?]+)',c[2])
  if m:ledger[m[1]]=c
 for manifest in a.local_manifest:
  for r in json.loads(manifest.read_text()):
   if r.get('pdf')or r.get('file'):local[r.get('id',r.get('name'))]=Path(r.get('pdf')or r['file'])
 rows=[]
 for fid,c in ledger.items():
  r=remote.get(fid);path=local.get(fid)or local.get(c[1]);sha=None;pages=None
  if path and path.is_file():
   sha=hashlib.sha256(path.read_bytes()).hexdigest()
   if path.suffix.lower()=='.pdf':
    import fitz
    with fitz.open(path)as pdf:pages=len(pdf)
  rows.append({'書名':c[0],'雲端ID':fid,'仍在雲端清單':r is not None,'檔名符合':r is not None and r['title']==c[1],'本機雜湊符合':sha==c[4]if sha else None,'本機頁數符合':str(pages)==c[3]if pages else None})
 report={'雲端份數':len(remote),'帳本份數':len(ledger),'新增來源ID':sorted(remote.keys()-ledger.keys()),'帳本缺少於雲端ID':sorted(ledger.keys()-remote.keys()),'檔名不符數':sum(not r['檔名符合']for r in rows),'本機雜湊已核對數':sum(r['本機雜湊符合']is not None for r in rows),'本機雜湊不符數':sum(r['本機雜湊符合']is False for r in rows),'本機頁數不符數':sum(r['本機頁數符合']is False for r in rows),'限制':'雲端清單來自連接工具；本機雜湊核對不等於重新下載並核對遠端內容。本次未修改來源檔案。','明細':rows}
 a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='明細'},ensure_ascii=False))
if __name__=='__main__':main()
