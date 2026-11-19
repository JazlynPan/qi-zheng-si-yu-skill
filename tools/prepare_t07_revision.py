#!/usr/bin/env python3
"""執行：準備T07修訂預覽與舊全文，不改卡、不套用、不補卡。"""
import difflib
import hashlib
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'docs/檢查/丙丁戊己錯配逐筆複核.json').read_text())
rows=[];patch=[]
for item in source['明細']:
    if item['圖上讀值']=='未確認':continue
    path=ROOT/'qi-zheng-si-yu/knowledge'/item['卡片'];old=path.read_text()
    typ='歲殿'if item['卡片'].startswith('歲殿')else'登籍'
    pattern=r'(?<=\n'+typ+r'\n\n)[^\n]+'
    assert re.findall(pattern,old)==[item['現值']],item['卡片']
    new=re.sub(pattern,item['圖上讀值'],old,count=1)
    start,end=item['年欄頁碼'],item['科甲共值頁碼'];loc=str(start)if start==end else f'{start}–{end}'
    new,n=re.subn(r'《星學綱目正傳》第\d+(?:[–—-]\d+)?頁',f'《星學綱目正傳》第{loc}頁',new)
    assert n==1 and old!=new
    row=dict(item,擬列來源頁碼=loc,修訂狀態='未授權、未套用',舊全文=old,擬修訂全文=new,舊SHA256=hashlib.sha256(old.encode()).hexdigest(),擬新SHA256=hashlib.sha256(new.encode()).hexdigest())
    rows.append(row)
    name='qi-zheng-si-yu/knowledge/'+path.name
    patch.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name))
assert len(rows)==21
output={'事項':'【勘校修正】T07預覽，尚未套用','限制':'只準備21張卡的值與來源頁碼修訂；己丑未確認不動，不新增或刪除卡，不改其他文字。','來源':'docs/檢查/丙丁戊己錯配逐筆複核.json','明細':rows}
folder=ROOT/'docs/待裁決'
(folder/'T07修訂預覽與舊全文.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
(folder/'T07修訂預覽.patch').write_text(''.join(patch))
lines=['# T07修訂預覽（尚未套用）','','21張卡只有擬改值與PDF來源頁碼；己丑未確認不動，沒有補卡。舊卡全文、擬修訂全文與SHA256已保存，預覽不會修改knowledge/。','','[逐筆原圖與定位](../檢查/丙丁戊己錯配逐筆複核.md)｜[舊全文與擬修訂全文](T07修訂預覽與舊全文.json)｜[完整差異](T07修訂預覽.patch)','','|卡片|現值|擬改字|擬列PDF頁碼|','|---|---|---|---|']
for x in rows:lines.append(f'|{x["卡片"]}|{x["現值"]}|{x["圖上讀值"]}|{x["擬列來源頁碼"]}|')
lines+=['','使用者確認後才可套用；執行時再次核對舊SHA256。修改另作提交，補卡另列、另作提交。']
(folder/'T07修訂預覽.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'預覽卡數':len(rows),'卡片異動數':0,'補卡數':0},ensure_ascii=False))
