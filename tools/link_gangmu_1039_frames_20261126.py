"""執行：核對1039框原圖雜湊，連回既有人工字框與現有卡；只做E0位置證據，不判字。"""
from review_helpers import *
from collections import Counter
stem='綱目1039框原圖與既有字框-2026-11-26';j=json.loads((D/'階段1.5原37頁1358段文字線索-2026-11-25.json').read_text());frames=[r for r in j['逐段'] if r['書名']=='星學綱目正傳'];assert len(frames)==1039
proofs=[];sources={};missing=[]
for n in range(73,97):
 name=f'綱目{n}頁餘下表續核稿-2026-11-20.json' if n<75 else f'綱目{n}頁下表續核-逐字稿-2026-11-21.json'
 data=json.loads((D/name).read_text())
 for r in data['明細']:
  proofs.append({'頁':n,'人工框':r['題字像素框'],'圖':r['原圖'],'卡片':r['卡名'],'原圖SHA256':r.get('原頁SHA256',r.get('來源SHA256')),'報告':name})
for pattern in ['綱目*細字續核-2026-11-25.json','綱目84頁伏尸旁字再核-2026-11-25.json','綱目98三欄下注續核-2026-11-25.json']:
 for p in D.glob(pattern):
  data=json.loads(p.read_text())
  for r in data.get('明細',[]):
   boxes=r.get('紅框')
   if not boxes:continue
   proofs.append({'頁':r['頁'],'人工框':boxes[0],'圖':r['紅框圖'],'卡片':r['卡片'],'原圖SHA256':r['原圖SHA256'],'報告':p.name})
for r in frames:
 n=r['PDF實際頁碼']
 if n not in sources:
  path=Path('/workspace/review/ocr')/r['原圖檔名'];sha=hashlib.sha256(path.read_bytes()).hexdigest();raw=json.loads((ROOT/r['候選來源']).read_text());assert raw['原圖SHA256']==sha
  sources[n]={'頁':n,'原圖檔名':path.name,'原圖SHA256':sha,'與原OCR來源雜湊一致':True,'框數':0}
 sources[n]['框數']+=1
for p in proofs:
 if not (PIC.parent.parent.parent/p['圖']).exists():assert (ROOT/p['圖']).exists()
 assert (K/p['卡片']).exists()
 assert p['原圖SHA256']==sources[p['頁']]['原圖SHA256'],('人工圖框來源不同',p['頁'],p['報告'])
rows=[]
for r in frames:
 poly=r['原框'];box=fitz.Rect(min(x[0]for x in poly),min(x[1]for x in poly),max(x[0]for x in poly),max(x[1]for x in poly));hits=[]
 for p in proofs:
  if p['頁']!=r['PDF實際頁碼']:continue
  b=fitz.Rect(p['人工框']);a=(box&b).get_area();small=min(box.get_area(),b.get_area());ratio=a/small if small else 0
  if ratio>=.5:
   card=K/p['卡片'];hits.append({**p,'矩形交集除較小框面積':round(ratio,4),'目前卡片SHA256':hashlib.sha256(card.read_bytes()).hexdigest()})
 rows.append({'id':f'GM{r["PDF實際頁碼"]}-{r["框序號"]:02d}',**r,'來源圖雜湊已核對':True,'可定位的既有人工字框':hits,'狀態':'已有相交人工字框，只供接續定位；不是整框核字通過' if hits else '本字框表尚無相交證據，需續接其他裁決／圖註或看原圖','限制':'交疊不等於原字、年組、取右左已確認；卡已經修改時仍以現卡與正式勘校紀錄為準，不拿舊手稿覆寫'})
report={'日期':'2026-11-26','證據等級':'E0，來源雜湊與矩形位置對照','圖頁數':len(sources),'原框數':len(rows),'原圖雜湊一致頁數':len(sources),'人工字框證據數':len(proofs),'框狀態數':dict(Counter(r['狀態'] for r in rows)),'卡片異動':0,'來源明細':list(sources.values()),'明細':rows,'限制':'這是既有資料的定位整理，尚不是1039框逐字核銷；上表、T07、擎遊左右、窄欄與頁碼裁決仍須接入，不以位置命中數算完成率。'}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目1039框原圖與既有字框','','## 結果','','26頁、1,039框的原圖SHA256均與當時OCR來源一致，可沿用框位；不是換過原圖後套舊座標。','連接24頁下表手稿及本輪細字等人工字框，只用來找到已收字位，不能由矩形交疊認定完整OCR框已核對。','','|項目|數量|','|---|---|',f'|原圖雜湊一致|{len(sources)}/{len(sources)}|',f'|既有人工字框|{len(proofs)}|']
for key,value in report['框狀態數'].items():md.append(f'|{key}|{value}|')
md+=['','## 接續方式','','先接上表及T07正式裁決與圖註；已收的字用現有卡，不照舊手稿回填舊值。沒有相交證據也不直接叫缺卡，可能是尚未接上的題字或上表，需看原圖。','[1,039框座標、原圖雜湊及卡片連結資料]('+stem+'.json)。本腳本不改卡，不新增概念，不作階段2分類。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({k:report[k] for k in ['圖頁數','原框數','原圖雜湊一致頁數','人工字框證據數','框狀態數','卡片異動']},ensure_ascii=False))
