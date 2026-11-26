"""執行：彙整盤圖人工記錄及文字層原句與同頁卡片的對照，不改卡。"""
from review_helpers import *
from collections import Counter
stem='命海124框來源與覆核-2026-11-26';base=json.loads((D/(stem+'-來源分流.json')).read_text());manual=json.loads((D/(stem+'-人工判讀稿.json')).read_text());byid={r['id']:r for r in manual['明細']}
pool={n:[] for n in range(331,337)}
for p in K.glob('*.md'):
 text=p.read_text();refs=SOURCE.findall(text)
 for n in pool:
  if any(b=='星平總會命海' and int(a)<=n<=int(z or a) and u=='頁' for b,a,z,u in refs):pool[n].append((str(p.relative_to(ROOT)),norm(text+p.name)))
def fold(text):return norm(text).replace('洩','泄')
rows=[]
for r in base['明細']:
 n=r['PDF實際頁碼']
 if r['id'] in byid:
  decision=byid[r['id']];evidence='本代理看原圖；已裁決文字沿用T15，不是獨立盲評'
 else:
  assert r['來源分流']=='文字層範圍，原句另核'
  native=r['原PDF文字層截取'];text=norm(native);variants=[];hits=[];missing=[]
  if '公众号' in native or 'bilibili' in native or native.isdigit():
   decision={'分類':'F','看圖紀錄':'編者聯絡資訊／印刷頁碼，非命理概念，不出卡。'}
  else:
   for segment in re.split(r'[，。；！？、：,.!?;:\n]+',native):
    key=norm(segment)
    if len(key)<2:continue
    matched=[path for path,stored in pool[n] if key in stored]
    if not matched:
     matched=[path for path,stored in pool[n] if fold(key) in fold(stored)]
     if matched:variants.append({'原文':segment,'對照':'洩／泄僅比對，不改原字'})
    if matched:
     hits.append({'原句片段':segment,'對應卡片':matched})
    else:missing.append(segment)
   decision={'分類':'B' if not missing else 'V','看圖紀錄':'原PDF文字層原句已在同頁卡片中分段保存；這是E0文字對照，不是OCR正確率。' if not missing else '原PDF文字層仍有片段未逐字命中，保留待核，不自動補卡。','原句片段對照':hits,'未命中片段':missing,'字形對照':variants}
  evidence='E0：PDF文字層幾何定位及原句與卡片對照，不作圖中文字裁決'
 rows.append({**r,**decision,'判讀依據':evidence})
assert len(rows)==124 and len({r['id'] for r in rows})==124
counts=dict(Counter(r['分類'] for r in rows));summary={str(n):dict(Counter(r['分類'] for r in rows if r['PDF實際頁碼']==n)) for n in range(331,337)}
info={'日期':'2026-11-26','總框數':124,'全部已具處理紀錄':124,'分類數':counts,'分類說明':{**manual['符號'],'B':'文字層原句分段已有同頁卡片（E0）','F':'編者資訊／印刷頁碼，不出卡','V':'文字層片段仍待核'},'逐頁':summary,'新增卡數':0,'既有卡異動':0,'限制':'124框都有去向，不是原圖所有字形都已確認；U、P、V不得宣告結案。T15已核定字不重問，圖糊022／024不重新要求猜字。原生盤圖僅410–416像素寬。','明細':rows}
(D/(stem+'-結果.json')).write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
md=['# 命海第331–336頁124框來源與覆核','','目錄：[結果](#結果)｜[逐頁](#逐頁)｜[逐框](#逐框)｜[仍待核](#仍待核)','','## 結果','','124框已全部有處理紀錄，分清原PDF文字層與盤內圖字；不是全部圖字已辨明。61框為文字層範圍，63框為盤圖內候選。文字層用原句對同頁卡，不把OCR誤讀當缺卡；盤內字逐框看圖並沿用使用者T15裁決。','','|類別|框數|說明|','|---|---|---|']
for code,label in info['分類說明'].items():
 if counts.get(code):md.append(f'|{code}|{counts[code]}|{label}|')
md+=['','## 逐頁','','|PDF頁|原框數|結果分布|','|---|---|---|']
for n,c in summary.items():md.append(f'|{n}|{sum(c.values())}|{json.dumps(c,ensure_ascii=False)}|')
md+=['','文字層的洩／泄差異僅用於對照，不改卡。不把其他書的命例或推算規律用來填星位、宿度。','[原生圖尺寸及限制](命海六盤原生解析度續核-2026-11-25.md)；[既有T15裁決](完整裁決執行總報告-2026-11-20.md)；[逐句對照與原框](命海124框來源與覆核-2026-11-26-結果.json)。','','## 逐框','','|編號|類別|紀錄|原圖|','|---|---|---|---|']
for r in rows:md.append(f'|{r["id"]}|{r["分類"]}|{r["看圖紀錄"]}|[紅框](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','## 仍待核','','原生像素無法支持的字不補；U保留未取定，P沿用既有疑註或待裁決。T15-016、032、075及既有三條疑註，不因文字對照命中而結案。','本報告不把原37頁1,358框全數宣告完成；與河洛195框合計319框已有逐項紀錄，其餘綱目1,039框仍須銜接人工與裁決紀錄。']
md+=['','## 保留字位','','|編號|頁|原因|圖|','|---|---|---|---|']
for row in rows:
    if row['分類'] in ['U','P','V']:md.append(f'|{row["id"]}|{row["PDF實際頁碼"]}|{row["看圖紀錄"]}|[紅框](../{row["紅框圖"].removeprefix("docs/")})|')
(D/(stem+'-結果.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({'總框':124,'分類':counts,'未命中':[(r['id'],r['未命中片段']) for r in rows if r['分類']=='V']},ensure_ascii=False))
