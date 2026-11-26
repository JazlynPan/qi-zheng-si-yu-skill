"""執行：依人工讀字生成31張擬新增卡的全文與SHA256；不建立knowledge卡、不推導值。"""
from review_helpers import *
stem='登籍31組補卡預覽-2026-11-26';data=json.loads((D/(stem+'-圖源.json')).read_text());read=json.loads((D/(stem+'-人工讀字.json')).read_text());reads={r['編號']:r for r in read['明細']};rows=[]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
for r in data['明細']:
 rr=reads[r['編號']];year=r['年份'];value=rr['原圖小字'];name=f'登籍圖列·{year}（星學綱目圖說下）.md';assert not (K/name).exists()
 for part in r['原始圖位證據']:
  src=Path('/workspace/review/ocr')/part['來源檔名'];assert hashlib.sha256(src.read_bytes()).hexdigest()==part['來源SHA256']
 low=min(r['年欄頁'],r['科甲欄頁']);high=max(r['年欄頁'],r['科甲欄頁']);span=str(low) if low==high else f'{low}–{high}'
 body=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{span}頁：\n\n原文以圖表呈現\n\n登籍\n\n{value}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
 assert all(body.count('## '+title)==1 for title in ['核心概念','使用規則','操作步驟','原文例子'])
 assert not any(body==p.read_text() for p in K.glob('登籍圖列·*.md'))
 images=[r['本次雙框']]
 if r['編號'] in ['DJ-25','DJ-26']:
  images.append('docs/待裁決/原圖/'+stem+'/'+r['編號']+'-擴至表底.png')
 rows.append({'編號':r['編號'],'年份':year,'原圖小字':value,'題字':rr['登籍題字'],'引用頁範圍':span,'年頭說明':rr['年頭說明'],'版式說明':rr['版式說明'],'擬新增卡名':name,'擬新增全文':body,'擬新增SHA256':hashlib.sha256(body.encode()).hexdigest(),'原圖':images,'原始圖位證據':r['原始圖位證據'],'自檢':{'有書名頁碼':True,'四欄完整':True,'不是僅頁碼空殼':True,'沒有同名現卡':True},'套用狀態':'未套用；原圖讀字與補卡仍待使用者確認'})
assert len(rows)==31 and all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items())
report={'日期':'2026-11-26','本批組數':31,'本代理已讀小字':31,'使用者已確認本批補卡':0,'待確認年頭有損': ['DJ-21戊申'],'來源圖需擴框者':['DJ-25丙辰','DJ-26丁巳'],'正式新增卡數':0,'既有卡異動':0,'全庫正式卡數':len(before),'限制':'只有預覽，不能當作31筆已獲使用者裁決；不得用源圖無字的戊寅、己丑或另被禁止補建的丙子來湊數，本批不包含這些組。DJ-21年頭有損須在確認時一併核年組。','明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 登籍31組補卡預覽','','## 現在完成什麼','','31組年頭與登籍題字／小字已直接看原圖，擬新增全文與SHA256都已備好。**只是預覽，正式新增0張，使用者尚未確認本批補卡。** 不看歲殿卡推值，也不套干支偏移。','DJ-25丙辰、DJ-26丁巳原框截得太短，已擴至表底才讀值；丁巳上下分列，不一律寫左右聯列。DJ-21戊申年頭局部有損，確認補卡時需一併看年組，不冒充原年頭全字清楚。','','## 逐組預覽','','|編號|年份|原圖讀字候選|PDF頁|原圖|','|---|---|---|---|---|']
for r in rows:
 links='／'.join(f'[圖{i+1}](../{x.removeprefix("docs/")})' for i,x in enumerate(r['原圖']))
 md.append(f'|{r["編號"]}|{r["年份"]}|{r["原圖小字"]}|{r["引用頁範圍"]}|{links}|')
md+=['','## 完整卡片預覽','','[31份擬新增全文與SHA256]('+stem+'.json)。正式卡數仍20,387張，不把本檔中的預覽計入knowledge/。新卡將只含原圖登籍題字與小字、書名頁碼及四欄缺載標記，不加自行推算的規則。','','## 需要使用者決定','','請確認上表讀字與年組，並明確同意哪些組可以補卡。可以一次同意全部31組，也可以排除DJ-21或另列不確定組；沒有同意前不新增。','本批只處理已備圖的31個缺登籍組；不把其他兩卡皆缺的組自動補齊，也不改歲殿卡。戊寅、己丑原圖空白維持原決定，丙子禁止新增範圍維持不動。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({'已讀候選':31,'正式新增':0,'既有卡異動':0,'正式卡數':len(before)},ensure_ascii=False))
