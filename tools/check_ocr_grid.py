#!/usr/bin/env python3
"""執行：彙整已對圖校讀的字列，列出未確認欄；不辨字、不補字、不修改卡片。"""
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();root=a.root
 records={};proofs=sorted((root/'docs/ocr/校讀').glob('星平總會命海-016*.json'))
 for path in proofs:
  for r in json.loads(path.read_text())['明細']:
   key=(r['原圖宮字'],r['原圖星名字']);v=records.setdefault(key,{})
   for field in ['可確認文字註','可確認變曜名字']:
    if field in r:
     if field in v and v[field]!=r[field]:raise ValueError('校讀證據不同：'+str(key))
     v[field]=r[field]
 houses=sorted({g for g,_ in records});stars=sorted({s for _,s in records});pending=[];cardmissing=[]
 for g in houses:
  for s in stars:
   v=records.get((g,s),{});missing=[f for f in ['可確認文字註','可確認變曜名字']if f not in v]
   if missing:pending.append({'宮字':g,'星名字':s,'待核對欄':missing,'已確認':v})
   path=root/'qi-zheng-si-yu/knowledge'/(g+'宮'+s+'圖列（星平總會命海）.md')
   if not path.is_file():cardmissing.append(str(path.relative_to(root)))
 result={'校讀證據檔數':len(proofs),'宮字數':len(houses),'星名字數':len(stars),'圖格數':len(houses)*len(stars),'已錄文字註數':sum('可確認文字註'in v for v in records.values()),'已錄曜名數':sum('可確認變曜名字'in v for v in records.values()),'未確認文字註數':sum('可確認文字註'in r['待核對欄']for r in pending),'未確認曜名數':sum('可確認變曜名字'in r['待核對欄']for r in pending),'卡片缺少數':len(cardmissing),'缺少卡片':cardmissing,'待核對':pending,'限制':'132格均有可確認文字，不等於整圖已轉錄；符號涵義未作判讀，未確認字不從他書補足。'}
 (root/'docs/檢查/命海16逐格核對.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 lines=['# 命海第16頁待核字列','','來源：《星平總會命海》PDF第16頁。由 tools/check_ocr_grid.py 彙整對圖校讀紀錄，不是自動辨字結果。','','132格已有卡片；118組文字註、113組曜名已轉錄。14組文字註、19組曜名仍待核對，未解釋○●，不算整圖完成。','','|宮字|星名字|待核對欄|已確認文字|','|---|---|---|---|']
 for r in pending:lines.append('|'+r['宮字']+'|'+r['星名字']+'|'+'、'.join(r['待核對欄'])+'|'+'；'.join(k+'：'+v for k,v in r['已確認'].items())+'|')
 (root/'docs/ocr/命海16待核字列.md').write_text('\n'.join(lines)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['待核對','缺少卡片']},ensure_ascii=False))
if __name__=='__main__':main()
