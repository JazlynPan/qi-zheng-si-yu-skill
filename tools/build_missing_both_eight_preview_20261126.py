"""執行：把八組原圖人工讀字存成擬新增全文；保留歲駕異題，不改卡。"""
from review_helpers import *
stem='其餘八組歲殿登籍原圖-2026-11-26';data=json.loads((D/(stem+'-圖源.json')).read_text());manual=json.loads((D/(stem+'-人工讀字.json')).read_text());read={r['編號']:r for r in manual['明細']};rows=[];cards=[]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in K.glob('*.md')}
for r in data['明細']:
 m=read[r['編號']];year=r['年份'];value=m['原圖小字候選'];low=min(r['年欄頁'],r['值欄頁']);high=max(r['年欄頁'],r['值欄頁']);span=str(low) if low==high else f'{low}–{high}';candidate=[]
 for topic in [m['上方原題候選'],m['另一原題']]:
  name=f'{topic}圖列·{year}（星學綱目圖說下）.md';assert not (K/name).exists()
  body=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{span}頁：\n\n原文以圖表呈現\n\n{topic}\n\n{value}\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
  candidate.append({'卡名':name,'擬新增全文':body,'擬新增SHA256':hashlib.sha256(body.encode()).hexdigest()});cards.append(name)
 rows.append({**r,**m,'來源頁範圍':span,'擬新增卡':candidate,'套用狀態':'候選，未獲使用者確認，不寫入knowledge'})
assert len(cards)==16 and len(set(cards))==16 and all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items())
report={'日期':'2026-11-26','本批組數':8,'擬新增卡數':16,'擬卡題名分布':{'歲殿':7,'歲駕':1,'登籍':8},'正式新增卡':0,'既有卡異動':0,'排除':'丙子使用者禁止新增；戊寅、己丑空白維持原決定，不在本批。八組均不在另一31組預覽內。','限制':'本代理讀字候選，不是使用者已核定。戊午題字候選歲駕，不把它當歲殿同義或補成歲殿。','明細':rows}
(D/(stem+'-預覽.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 其餘八組歲殿、登籍原圖與補卡預覽','','## 結果','','回查現在兩張題名卡皆缺的九組：丙子依使用者禁止新增，直接排除；其餘八組原圖已看，備16份擬新增全文，**正式新增0張**。本批與31組缺登籍分開。','戊午原題下半較像馬部，候選為歲駕；不把歲駕當歲殿同義，不建歲殿戊午卡。己亥小字略淡，候選辰仍須看圖確認。','','|編號|年份|原題候選|小字候選|PDF頁|圖|','|---|---|---|---|---|---|']
for r in rows:md.append(f'|{r["編號"]}|{r["年份"]}|{r["上方原題候選"]}／登籍|{r["原圖小字候選"]}|{r["來源頁範圍"]}|[雙框](../{r["原圖"].removeprefix("docs/")})|')
md+=['','## 尚未套用','','[16份擬新增卡全文、原圖SHA256及候選說明]('+stem+'-預覽.json)。只有使用者明確確認的組與題名才可補；不同意或不清的保留未確認。','戊寅與己丑原圖空白不補，丙子禁止新增不再詢問。31組另見[登籍補卡預覽](登籍31組補卡預覽-2026-11-26.md)。']
(D/(stem+'-預覽.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({'八組擬卡':16,'正式新增':0,'歲駕不等同歲殿':True},ensure_ascii=False))
