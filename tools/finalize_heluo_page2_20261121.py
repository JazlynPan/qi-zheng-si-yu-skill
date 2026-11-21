"""執行：保存原圖0之39框人工接續結果、原文補錄與復工位置；不再改卡。
目錄：人工判讀分流；報告；進度；新舊卡檢查。
"""
from pathlib import Path
from collections import Counter
import json,hashlib,re
R=Path(__file__).resolve().parents[1];D=R/'docs/檢查';p=D/'河洛第2頁原圖0之39框位置對照-2026-11-21.json';j=json.loads(p.read_text())
seen={2:('既有片段已收','將爵對照'),3:('既有片段已收','命主入垣'),5:('既有片段已收','官魁拱命'),6:('原字新補','井'),8:('原字新補','魁星'),10:('原字新補','參'),19:('既有片段已收','將星'),24:('紅筆小框不作文字',''),27:('部分片段新補，非全框核畢','土虛十；國印')}
manual=[]
for x in j['明細']:
 if not x['新紅框']:continue
 n=int(x['編號'].split('-')[-1]);status,reading=seen.get(n,('旋斜／紅筆重疊，未確認',''));x['人工接續結果']=status;x['人工讀值']=reading;manual.append(x)
j['人工接續統計']=dict(Counter(x['人工接續結果']for x in manual));j['限制']='機械交疊結果保留原數，另列23張原圖人工覆核；不以交疊率判原文正確或全頁覆蓋。';p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
p=D/'河洛第2頁原圖0之39框位置對照-2026-11-21.md';s=p.read_text();marker='## 23張位置圖人工接續結果';extra=['',marker,'',str(j['人工接續統計'])+'。這23張的人工結果與機械位置交疊分開，不是23項新問題。','','|編號|人工接續|原字（未確認者不填）|','|---|---|---|']
for x in manual:extra.append(f'|{x["編號"]}|{x["人工接續結果"]}|{x["人工讀值"]}|')
extra+=['','僅定字井、魁星、參三段新補至原命例，未賦予星曜或宮位含義。第27框只收已確認土虛十、國印，周邊其他字不算完成。','下一個第一動作：HL2-0-11及12同一斜字區，先按四方向核字並對照相鄰完整字；其餘12處未確認框續排在後，原圖1也尚未全頁核銷。']
if marker not in s:s+='\n'.join(extra)+'\n'
if len(s.splitlines())>100 and '## 目錄'not in s:s=s.replace('\n\n','\n\n## 目錄\n\n- [39框位置表](#39框位置表)\n- [23張位置圖人工接續結果](#23張位置圖人工接續結果)\n\n## 39框位置表\n\n',1)
p.write_text(s)
p=R/'docs/狀態.md';s=p.read_text();s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛五星合參案例抄本》第2頁新增5片段至原命例，54候選框已作現卡核銷，原圖0之39框已作位置對照及23張圖人工分流。下一個第一動作：HL2-0-11／12斜字區四方向核字，仍不明則保留；原圖1覆蓋未完成。',s,1);p.write_text(s)
p=R/'docs/catalog/河洛五星合參案例抄本.md';s=p.read_text();note='\n39框位置圖已另作23張人工接續分流：4張既有文字、3張新補原字、1張紅筆小框不當文字、1張部分片段已補、14張旋斜／重疊未確認。[逐框結果](../檢查/河洛第2頁原圖0之39框位置對照-2026-11-21.md)。不宣告整頁完成。\n'
if '39框位置圖已另作23張人工接續分流'not in s:s+=note
p.write_text(s)
p=R/'tools/review_heluo_page2_20261121.py';s=p.read_text();s=s.replace('本輪新看原圖僅024','本輪新看024及39框位置圖').replace('本次只追加T17-024的「土虛十」「國印」兩片段','本次追加T17-024的「土虛十」「國印」，以及39框續核的「井」「魁星」「參」，共5片段').replace('只追加「土虛十」「國印」兩原文片段','只追加「土虛十」「國印」「井」「魁星」「參」5原文片段').replace('第024框新核「土虛十」「國印」，僅追加','第024框及39框新核土虛十、國印、井、魁星、參共5片段，僅追加').replace('第2頁T17-024另核土虛十、國印兩片段','第2頁另核土虛十、國印、井、魁星、參5片段');p.write_text(s)
e=json.loads((R/'docs/勘校修訂/河洛2頁續核-2026-11-21/舊新全文與SHA256.json').read_text());card=(R/'qi-zheng-si-yu/knowledge'/e['卡片']).read_text();assert card.startswith(e['舊全文'])and hashlib.sha256(card.encode()).hexdigest()==e['新SHA256'];assert all(card.count('## '+f)==1 for f in ['核心概念','使用規則','操作步驟','原文例子']);print(json.dumps(j['人工接續統計'],ensure_ascii=False));print('舊全文完整前綴及新卡SHA256、四欄檢查通過。')
