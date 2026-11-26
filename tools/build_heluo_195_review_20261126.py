"""執行：串接已存原圖核讀與本次人工判讀稿，產生195框結果；不自動判字、不改卡。"""
from pathlib import Path
from collections import Counter
import json
R=Path(__file__).resolve().parents[1];D=R/'docs/檢查';stem='河洛195段逐框覆核-2026-11-26'
base=json.loads((D/(stem+'-原框.json')).read_text());manual=json.loads((D/(stem+'-人工判讀稿.json')).read_text());byid={r['id']:r for r in manual['明細']}
p2old=json.loads((D/'河洛第2頁原圖0之39框位置對照-2026-11-21.json').read_text());p2latest=json.loads((D/'河洛第2頁斜排續核-2026-11-25.json').read_text());t17=json.loads((D/'河洛第2頁54候選框核銷-2026-11-21.json').read_text())
p2={int(r['編號'].split('-')[-1]):r for r in p2old['明細']};latest={int(r['編號'].split('-')[-1]):r for r in p2latest['明細']};t17map={r['編號']:r for r in t17['明細']}
p3old=json.loads((D/'河洛第3頁39框分區覆核-2026-11-25.json').read_text());p3={int(r['編號'].split('-')[-1]):r for r in p3old['明細']}
rows=[]
for r in base['明細']:
 n=r['PDF實際頁碼'];i=r['框序號'];poly=r['原框'];box=[min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]
 if n==2:
  old=p2[i];assert old['原框']==box
  evidence=['河洛第2頁原圖0之39框位置對照-2026-11-21.json'];fragments=[]
  if i in latest:
   last=latest[i];assert last['原框']==box
   code='C' if last['讀值'] else 'U';note=last['結果']+('：'+last['讀值'] if last['讀值'] else '')
   evidence.append('河洛第2頁斜排續核-2026-11-25.json')
  elif old.get('人工接續結果'):
   code='S' if any(w in old['人工接續結果'] for w in ['紅筆','符號','空白']) else 'C';note=old['人工接續結果']+'；'+str(old.get('人工讀值',''))
  elif old['位置交疊']:
   for ident in old['位置交疊']:
    for f in t17map[ident].get('核對片段',[]):
     if f['片段'] not in fragments:fragments.append(f['片段'])
   assert fragments
   code='C' if len(fragments)==1 else 'X';note='沿用前次已核原列片段；不是說OCR候選整串正確。'+ '／'.join(fragments)
   evidence.append('河洛第2頁54候選框核銷-2026-11-21.json')
  else:
   code='U';note='原圖框仍無完整可確認讀序，保留未確認，不猜。'
  decision={'分類':code,'看圖紀錄':note,'依據報告':evidence,'沿用已核片段':fragments}
 elif n==3:
  old=p3[i];assert old['原框']==box
  code='C' if '原字可辨' in old['結果'] else 'S'
  decision={'分類':code,'看圖紀錄':old['結果']+('：'+old['可辨原字'] if old['可辨原字'] else ''),'依據報告':['河洛第3頁39框分區覆核-2026-11-25.json']}
 else:
  decision=byid[r['id']];decision={**decision,'依據報告':[stem+'-人工判讀稿.json']}
 assert (R/r['紅框圖']).exists()
 rows.append({**r,'覆核狀態':decision['分類'],**decision})
assert len(rows)==195 and len({r['id'] for r in rows})==195
counts=dict(Counter(r['分類'] for r in rows));by_page={str(n):dict(Counter(r['分類'] for r in rows if r['PDF實際頁碼']==n)) for n in [2,3,12,13,15]}
report={'日期':'2026-11-26','總框數':195,'已有逐框處理紀錄':195,'分類數':counts,'逐頁分類':by_page,'說明':manual['符號'],'範圍':base['範圍'],'卡片異動':'本彙整腳本0；本次另有第13頁比肩、木胃原文續錄1張，見專項報告','限制':'195框都有結果，不等於195框字都已辨明；U與P仍未結案。C也不表示OCR原候選全文正確。不是獨立代理盲評。','明細':rows}
(D/(stem+'-結果.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 河洛195段逐框覆核','','目錄：[結果](#結果)｜[逐頁](#逐頁)｜[逐框](#逐框)｜[未結案](#未結案)','','## 結果','','195個原框均已有處理紀錄；不是195框字形全部辨明，也不是全圖、全部角度候選都已驗收。','第2、3頁沿用既有逐框判讀，框位逐一一致才接入；第12、13、15頁本次直接看圖與第13頁四方向圖，沒有用候選倒填原文。','','|結果|框數|','|---|---|']
for code,label in manual['符號'].items():md.append(f'|{label}|{counts.get(code,0)}|')
md+=['','## 逐頁','','|PDF頁|總框|C|S|X|U|P|','|---|---|---|---|---|---|---|']
for n,c in by_page.items():md.append('|'+n+'|'+str(sum(c.values()))+'|'+'|'.join(str(c.get(x,0)) for x in ['C','S','X','U','P'])+'|')
md+=['','本表C是已收片段，S是無獨立敘述的圖題／單字／符號，X是跨格，U是仍未取定字，P是既有待裁決。這是原圖框的工作紀錄，不是階段2的卡片分類。','[第13頁比肩、木胃續錄](河洛13頁比肩木胃續錄-2026-11-26.md)只追加原命例，後接數字未填。','','## 逐框','','|編號|結果|看圖紀錄|原圖|','|---|---|---|---|']
for r in rows:md.append(f'|{r["id"]}|{r["分類"]}|{r["看圖紀錄"].replace(chr(10)," ").replace("|","／")}|[紅框](../{r["紅框圖"].removeprefix("docs/")})|')
md+=['','## 未結案','','U、P各項見上表與[完整資料]('+stem+'-結果.json)。這些項目不新建僅有頁碼的卡，也不改原卡猜字。','候卦未濟／未逢仍等HL15-候卦裁決；T17-119圖糊依指示保留。字形才／財、台／臺只在證據中保留對照，不因此批量替換。','原37頁總數1,358框，本報告只涵蓋其中河洛195框；其他1,163框仍須銜接其逐頁／逐框記錄，不把這份表當全37頁驗收。']
md+=['','## 需要使用者決定的字位','','每題只問：紅框內還能辨讀完整字嗎？選項：能（請填原字）／看不清（保留未確認）。既有HL15-候卦沿用原問題。','','|編號|頁|本次仍未定之處|圖|','|---|---|---|---|']
for row in rows:
    if row['分類']=='U':md.append(f'|{row["id"]}|{row["PDF實際頁碼"]}|{row["看圖紀錄"]}|[紅框](../{row["紅框圖"].removeprefix("docs/")})|')
(D/(stem+'-結果.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({'總框':195,'分類':counts,'逐頁':by_page},ensure_ascii=False))
