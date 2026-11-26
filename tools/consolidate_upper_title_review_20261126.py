"""執行：彙整151個未見題名位置的查核狀況；不是卡片分類，不改卡。"""
from review_helpers import *
from collections import Counter
stem='綱目上表151未見題名查核彙整-2026-11-26'
matrix=json.loads((D/'綱目上表題名存在性-2026-11-26.json').read_text())
tri=json.loads((D/'綱目跨頁右緣三元36格續核-2026-11-26.json').read_text())
last=json.loads((D/'綱目上表其餘32格原圖-2026-11-26-結果.json').read_text())
unread={}
for data,file in [(tri,'綱目跨頁右緣三元36格續核-2026-11-26.json'),(last,'綱目上表其餘32格原圖-2026-11-26-結果.json')]:
 for r in data['明細']:
  value=r.get('候選讀字',r.get('讀字候選'))
  if value is None:unread[(r['年組'],r['題名'])]={'報告':file,'原圖':r['原圖'],'原因':r.get('未定原因')or r.get('狀態')}
eth=json.loads((D/'綱目乙年頭右緣續核-2026-11-26.json').read_text())
for r in eth['祿勳待讀字']:unread[(r['年組'],'祿勳')]={'報告':'綱目乙年頭右緣續核-2026-11-26.json','原圖':r['原圖'],'原因':r['狀態']}
bingzi=json.loads((D/'綱目73丙子原欄20題讀圖-2026-11-26-結果.json').read_text())
for z in bingzi['明細']:
 if z['題名']=='玉堂':unread[('丙子','玉堂')]={'報告':'綱目73丙子原欄20題讀圖-2026-11-26-結果.json','原圖':z['原圖'],'原因':z['未定原因']}
rows=[]
for r in matrix['明細']:
 if r['精確檔名存在']:continue
 year=r['年組'];topic=r['題名'];name=r['檔名'];base={'年組':year,'題名':topic,'精確檔名':name}
 if r['已有完整預覽']:
  kind='完整候選預覽，未授權不補卡';evidence={'報告':r['已有完整預覽']}
 elif year=='丙子'and topic in ['歲殿','登籍']:kind='已確認寅值，本輪不新增';evidence={'報告':'綱目73丙子原欄20題讀圖-2026-11-26-結果.json','原因':'原有丙子寅值不新增決定維持；不擴張成20題永久禁補。'}
 elif topic in ['擎天','遊奕']:kind='原圖擎遊取側尚未裁決';evidence={'報告':'科甲欄全組重核.md','原因':'原圖未分單星時不替它選右或左，缺題名不構成填值授權。'}
 elif topic=='歲殿'and year in ['丁丑','己丑']:
  alt=f'歲駕圖列·{year}（星學綱目圖說下）.md';assert(K/alt).exists();kind='已有不同原題，或異題候選';evidence={'報告':'../catalog/星學綱目正傳.md','不同題名卡':alt,'SHA256':hashlib.sha256((K/alt).read_bytes()).hexdigest(),'原因':'有歲駕題名不等於歲殿缺卡，也不自行認作同義。'}
 elif topic=='歲殿'and year=='戊午':kind='已有不同原題，或異題候選';evidence={'報告':'其餘八組歲殿登籍原圖-2026-11-26-預覽.json','原因':'原題候選歲駕，完整預覽另存，不當作歲殿已覆蓋。'}
 else:
  assert (year,topic)in unread,(year,topic);kind='原字未全取定，保留圖證不製卡';evidence=unread[(year,topic)]
 rows.append({**base,'查核狀況':kind,**evidence})
counts=dict(Counter(r['查核狀況']for r in rows))
assert len(rows)==151 and sorted(counts.values())==[2,3,8,35,103]
report={'日期':'2026-11-26','精確題名未見位置':151,'各狀況數':counts,'所有位置均有查核狀況':True,'正式補卡':0,'卡片異動':0,'限制':'這是上表題名存在性後續的來源查核，不是151張漏卡，也不是階段2的卡片分類。尚未確認的候選與原圖字仍不得宣告完成。','明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目上表151個未見題名位置查核彙整','','## 目錄','','- [數量與限制](#數量與限制)','- [逐位置狀況](#逐位置狀況)','- [接續條件](#接續條件)','','## 數量與限制','','151是精確題名未見的檔名位置數，不是原圖漏收卡數；現在每個位置都有可追查的狀況。沒有把候選寫進正式卡，也沒有開始階段2。','','|狀況|位置數|','|---|---|']
md += [f'|{k}|{v}|'for k,v in counts.items()]
md+=['','## 逐位置狀況','','|年組|題名|查核狀況|證據|','|---|---|---|---|']
for r in rows:md.append(f'|{r["年組"]}|{r["題名"]}|{r["查核狀況"]}|[紀錄]({r["報告"]})'+(f' [原格](../{r["原圖"].removeprefix("docs/")})'if r.get('原圖')else'')+'|')
md+=['','## 接續條件','','103個位置已有完整候選，必須等使用者確認讀字與年組後才補；35個原字仍未全取定，保留圖證不建空殼。丙子歲殿、登籍2題原寅值仍不新增，不擴張成20題永久禁補；擎遊8個位置不自行取側；不同原題3個位置不自行混作同義。','', '每個位置有紀錄不等於原字全部已辨明，也不等於階段1.5已完成或已驗收。圖糊、切邊不得因其他書存在理論值便回填。','', '[完整資料與數量口徑]('+stem+'.json)。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'復工位置：[^\n]+','復工位置：《綱目》第97頁文昌欄下注1張已推送0c99e701。上表151個未見題名位置已各列查核狀況：103完整候選未回填、35原字未全定、2原寅值不新增、8擎遊待裁決、3原題不同。第97–98頁55框已有分流；十二跨頁來源候選另附並排圖。下一個第一動作：讀取使用者針對候選及原圖的明確裁決，只套用同意部分並保留舊文；未確認者不代填，不自行標記階段1.5完成。',s,1);p.write_text(s)
with (ROOT/'docs/catalog/星學綱目正傳.md').open('a')as f:f.write('\n### 2026-11-26：上表151位置查核彙整\n\n精確題名未見151位置均已具查核狀況：103完整候選、35未全取定、2原寅值不新增、8擎遊未定側、3不同原題；不是151張漏卡，不正式補卡。[逐位置證據](../檢查/'+stem+'.md)。\n')
print(json.dumps({'位置數':151,'狀況':counts,'正式補卡':0,'卡片異動':0},ensure_ascii=False))
