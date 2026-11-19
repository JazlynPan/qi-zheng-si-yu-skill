#!/usr/bin/env python3
"""執行：驗證2026-11-19綱目97–98頁續核批次；不改卡片。"""
import json
import re
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git','-c','core.quotepath=false',*args],cwd=ROOT).decode()
proof=json.loads((ROOT/'docs/ocr/校讀/星學綱目正傳-097祿勳文魁官印再核.json').read_text())
checks={}
checks['新卡3張']=len(proof['明細'])==3
for x in proof['明細']:
    text=(ROOT/'qi-zheng-si-yu/knowledge'/x['卡片']).read_text()
    checks[x['原題']+'四欄標籤出處']=text.startswith('#七政四餘\n') and all('## '+h in text for h in ['核心概念','使用規則','操作步驟','原文例子']) and '《星學綱目正傳》第97頁' in text
    checks[x['原題']+'照錄字列一致']='\n'.join(x['圖字逐列']) in text
changes=git('diff','--name-status','5eae8fe1','--','qi-zheng-si-yu/knowledge').splitlines()
checks['僅新增3卡無既有異動']=len(changes)==3 and all(x.startswith('A\t') for x in changes)
checks['全庫19763張']=len(list((ROOT/'qi-zheng-si-yu/knowledge').glob('*.md')))==19763
checks['報告提交卡片異動0']=not git('diff','46226433','--','qi-zheng-si-yu/knowledge').strip()
errors=[]
p=ROOT/'docs/檢查/綱目97至98頁續核紀錄.md'
for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
    # 此次執行產生的驗證檔於下方寫入，其餘檔案須已存在。
    if link=='綱目97至98頁續核驗證.json':continue
    if not(p.parent/link).exists():errors.append(link)
checks['報告來源連結可解析']=not errors
checks['OCR四欄及三欄結果齊全']=all(len(json.loads((ROOT/'docs/ocr/機器候選'/name).read_text())['結果'])==n for name,n in [('綱目97四欄再核-PaddleOCRv5.json',4),('綱目98三欄再核-PaddleOCRv5.json',3)])
checks['狀態30行內']=len((ROOT/'docs/狀態.md').read_text().splitlines())<=30
result={'日期':'2026-11-19','證據等級':'E0；不代表OCR字讀正確性或全頁驗收','通過':all(checks.values()),'檢查':checks,'失效連結':errors}
(ROOT/'docs/檢查/綱目97至98頁續核驗證.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if result['通過'] else 1)
