#!/usr/bin/env python3
"""執行：核對第98頁三欄右列批次的格式、原字照錄與既有卡不變性。"""
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROOF=ROOT/'docs/ocr/校讀/星學綱目正傳-098三欄右列字列.json'
p=json.loads(PROOF.read_text());checks={}
checks['三卡各12格']=len(p['明細'])==3 and all(len(x['右列逐格字列'])==12 for x in p['明細'])
for x in p['明細']:
    text=(ROOT/'qi-zheng-si-yu/knowledge'/x['卡片']).read_text()
    checks[x['原題']+'格式及出處']=text.startswith('#七政四餘\n') and all('## '+h in text for h in ['核心概念','使用規則','操作步驟','原文例子']) and '《星學綱目正傳》第98頁' in text
    checks[x['原題']+'右列原字與紀錄一致']='\n'.join(x['右列逐格字列']) in text
    checks[x['原題']+'原圖存在']=(PROOF.parent/x['原圖']).is_file()
changes=subprocess.check_output(['git','diff','--name-only','--diff-filter=MDR','77e0e36b','--','qi-zheng-si-yu/knowledge'],cwd=ROOT)
checks['既有卡片異動0']=not changes.strip()
checks['逐格接觸表存在']=(PROOF.parent/p['逐格接觸表']).is_file()
checks['未將整欄宣告完成']=all('仍待核' in x['狀態']for x in p['明細'])
result={'證據等級':'E0：格式、檔案與照錄紀錄比對；不代替原圖字讀驗收','通過':all(checks.values()),'檢查':checks}
(ROOT/'docs/檢查/綱目98右列字列驗證.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if result['通過']else 1)
