#!/usr/bin/env python3
"""執行：依人工核圖紀錄產生已核字列卡與驗證報告；--apply只建新卡，不覆寫。"""
import argparse
import hashlib
import json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1];folder=root/'qi-zheng-si-yu/knowledge'
source=root/'docs/ocr/校讀/星學綱目正傳-100伏尸闌干已核二十格.json';data=json.loads(source.read_text())
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in folder.glob('*.md')};new=[];checks={}
for row in data['明細']:
    path=folder/row['卡片']
    text='#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第100頁：\n\n原文以圖表呈現\n\n'+row['原題']+'\n\n'+'\n'.join(row['已核字列'])+'\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
    if not path.exists() and a.apply:path.write_text(text);new.append(path.name)
    checks[row['原題']+'卡片與核圖紀錄一致']=path.is_file() and path.read_text()==text
    checks[row['原題']+'原圖存在']=(source.parent/row['原圖']).is_file()
    checks[row['原題']+'只收十格']=len(row['已核字列'])==10 and len(row['未收原格'])==2
checks['既有卡逐位元組保留']=all(hashlib.sha256((folder/n).read_bytes()).hexdigest()==h for n,h in before.items())
checks['逐格圖存在']=(source.parent/data['逐格圖']).is_file()
result={'日期':data['日期'],'證據等級':'E0：格式與人工紀錄相符，不等於全頁驗收','通過':all(checks.values()),'檢查':checks,'本批卡片':[x['卡片'] for x in data['明細']],'限制':data['限制']}
(root/'docs/檢查/綱目100二十格驗證.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# 綱目100頁伏尸、闌干續核','','只收已確認的20格，未修改既有卡片；數字只照原字，不補成度數或其他單位。不是整欄完整提取，也未補使用方法。','','- [核圖原字與未收四格](../ocr/校讀/星學綱目正傳-100伏尸闌干已核二十格.json)','- [逐格原圖](../ocr/校讀原圖/綱目100宿名三欄逐格接觸表.png)','- [格式檢查](綱目100二十格驗證.json)']
for row in data['明細']:
    lines+=['','## '+row['原題'],'','已收：'+'、'.join(row['已核字列'])+'。','未收：'+'；'.join(row['未收原格'])+'。',f'[整欄放大圖](../ocr/校讀原圖/{Path(row["原圖"]).name})']
lines+=['','## 未完成','','貫索及兩欄未收四格仍待核，不建空殼卡。逐格接觸表是工作用裁切，跨格筆畫必須回整欄核讀，不能依裁切線補字。']
(root/'docs/檢查/綱目100伏尸闌干續核.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['通過']else 1)
