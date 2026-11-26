"""執行：彙整已讀原圖的104份補卡候選；不是正式索引，不寫knowledge。"""
from review_helpers import *
files=['登籍31組補卡預覽-2026-11-26.json','其餘八組歲殿登籍原圖-2026-11-26-預覽.json','綱目75乙丑未見題名原格-2026-11-26.json','綱目乙年頭右緣續核-2026-11-26.json','綱目跨頁右緣三元36格續核-2026-11-26.json','綱目上表其餘32格原圖-2026-11-26-結果.json','綱目73丙子原欄20題讀圖-2026-11-26-結果.json']
found={}
def walk(obj,parent,file):
 if isinstance(obj,list):
  for item in obj:walk(item,parent,file)
 elif isinstance(obj,dict):
  ctx={**parent,**{k:v for k,v in obj.items()if not isinstance(v,(list,dict))}}
  name=obj.get('擬新增卡名')or obj.get('卡名')
  if name and obj.get('擬新增全文'):
   body=obj['擬新增全文'];sha=hashlib.sha256(body.encode()).hexdigest();assert sha==obj['擬新增SHA256'];assert not(K/name).exists()
   image=ctx.get('本次雙框')or ctx.get('原圖')or ctx.get('紅框圖')
   if not image and isinstance(obj.get('原圖'),list):image=obj['原圖'][0]
   if not image:
    for z in obj.get('明細',[]):
     if z.get('題名')in name:image=z.get('原圖');break
   assert image and(ROOT/image).exists(),(name,image)
   m=re.search(r'圖列·([^（]+)',name);assert m;year=m[1];topic=name.split('圖列·')[0]
   raw=body.split('## 使用規則',1)[1].split('## 操作步驟',1)[0];cite=re.search(r'《[^》]+》第[^\n]+頁',raw)[0]
   parts=[s.strip()for s in raw.split('原文以圖表呈現',1)[1].splitlines()if s.strip()]
   if parts and parts[0]==year:parts.pop(0)
   if parts and parts[0]==topic:parts.pop(0)
   flag='年頭破損／歸組待確認'if year in ['戊申','丙子']else('原題歲駕仍待確認'if year=='戊午'and topic=='歲駕'else'候選可供逐項確認')
   assert name not in found
   found[name]={'卡名':name,'年組':year,'原題':topic,'來源':cite,'候選原字':' ／ '.join(parts),'原圖':image,'狀態':flag,'完整預覽檔':file,'擬新增全文':body,'擬新增SHA256':sha}
  for value in obj.values():
   if isinstance(value,(dict,list)):walk(value,ctx,file)
for file in files:walk(json.loads((D/file).read_text()),{},file)
rows=sorted(found.values(),key=lambda r:r['卡名']);assert len(rows)==104
safe=[r for r in rows if r['狀態']=='候選可供逐項確認'];held=[r for r in rows if r not in safe]
assert len(safe)==82 and len(held)==22
stem='綱目上表補卡候選總覽-2026-11-26'
report={'日期':'2026-11-26','完整候選份數':104,'一般候選份數':82,'年頭破損或原題待確認份數':22,'與151題名盤點的關係':'103份對應精確題名未見位置；另1份為原題候選歲駕戊午，不當歲殿。','正式新增':0,'卡片異動':0,'限制':'候選不是已核定卡。一般候選82份也要使用者確認才新增；不因本表整理完便視為授權。','明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目上表補卡候選總覽（2026-11-26）','','## 目錄','','- [數量與用途](#數量與用途)','- [逐項看圖](#逐項看圖)','- [需要使用者決定](#需要使用者決定)','','## 數量與用途','','104份完整候選全部在工作文件，正式新增0。103份對應151個未見題名位置；另1份歲駕戊午不當歲殿。一般候選82份；另22份有年頭破損或原題未定。**82份也尚未獲使用者確認，不會自動補卡。**','','每項連到原圖及其完整四欄預覽。雙字以原圖物理順序並列，不附加取用法；不清的字不在完整候選內，另列catalog。','','## 逐項看圖','','|編號|擬新增卡名|出處|候選原字|狀態|原圖／全文|','|---|---|---|---|---|---|']
for i,r in enumerate(rows,1):md.append(f'|{i:03d}|{r["卡名"].removesuffix(".md")}|{r["來源"]}|{r["候選原字"]}|{r["狀態"]}|[原圖](../{r["原圖"].removeprefix("docs/")}) [全文]({r["完整預覽檔"]})|')
md+=['','## 需要使用者決定','','1. 是否同意先補82份一般候選，22份年頭破損或原題未定者保留？','2. 也可只指定同意的編號；不同意的維持未確認。原寅值不新增的歲殿／登籍丙子兩題不在本104份。','', '[104份完整全文、SHA256及名單](綱目上表補卡候選總覽-2026-11-26.json)。授權後只新增同意的卡，不覆寫其他原文。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({'候選總覽':104,'一般候選':82,'需另確認':22,'正式新增':0},ensure_ascii=False))
