"""執行：將既有上表原圖定位與目前卡片引用對照；只列候選，不取原字、不改卡。"""
from review_helpers import *
from audit_kejia import layout
from collections import Counter
stem='綱目上表現卡與舊定位對照-2026-11-26';old=json.loads((D/'科甲欄全組重核.json').read_text());cy=json.loads((D/'催官貴元跨頁抽查.json').read_text());rows=[]
for source,data in [('科甲欄全組重核.json',old['明細']),('催官貴元跨頁抽查.json',cy['明細'])]:
 for r in data:
  name=r['卡名'];p=K/name;page=r['原圖實際頁碼'];path=Path('/workspace/review/ocr')/f'綱目-{page}-原圖0.png';im=Image.open(path);w,h=im.size;topic=name.split('圖列')[0];year=name.split('·')[1].split('（')[0]
  if source.startswith('科甲'):
   pp,x,yp,hx=layout(year);assert pp==page
   low,high={'空亡':(.15,.28),'擎天':(.25,.405),'遊奕':(.25,.405),'歲殿':(.34,.49),'登籍':(.34,.49)}[topic]
   if year=='丙辰' and topic in ['擎天','遊奕']:low,high=.25,.445
   bbox=[max(0,int((x-.075)*w)),int(low*h),min(w,int((x+.075)*w)),int(high*h)]
  else:bbox=r['紅框原像素座標']
  actual=[];sha=None;body=None
  if p.exists():
   body=p.read_text();sha=hashlib.sha256(p.read_bytes()).hexdigest()
   actual=[{'書名':b,'起頁':int(a),'迄頁':int(z or a)} for b,a,z,u in SOURCE.findall(body) if b=='星學綱目正傳' and u=='頁']
   status='目前引用涵蓋舊定位頁，並不代表字值已核定' if any(a['起頁']<=page<=a['迄頁'] for a in actual) else '目前引用未涵蓋舊定位頁，需回原圖確認是否頁碼問題'
  else:status='目前沒有此卡，不據原圖暫讀自動補建'
  if r.get('編號')=='CY-23':status='第四輪已撤銷錯補，貴元星名未確認；不恢復卡'
  assert (ROOT/r['原圖']).exists()
  rows.append({'編號':r['編號'],'題字':topic,'年份':year,'卡片':name,'存在':p.exists(),'現卡SHA256':sha,'目前引用':actual,'舊定位實際頁':page,'舊定位框':bbox,'舊原圖':r['原圖'],'原圖檔名':path.name,'目前原圖SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'沿用報告':source,'來源對照狀態':status,'限制':'只沿用既有定位函式或坐標；不是新的字值核定，不從年份公式推值、不復用舊卡值'})
counts=dict(Counter(r['來源對照狀態'] for r in rows));missing=[r for r in rows if r['存在'] and not any(a['起頁']<=r['舊定位實際頁']<=a['迄頁'] for a in r['目前引用'])]
report={'日期':'2026-11-26','證據等級':'E0，現卡引用範圍與舊原圖定位比較','上表筆數':len(rows),'狀態分布':counts,'引用範圍待核候選數':len(missing),'候選不是已確認錯誤':'舊定位仍可能有欄位或裁框問題；需回原圖，不自動改頁碼或補卡。CY-23依既有第四輪撤銷已同步。','卡片異動':0,'明細':rows}
(D/(stem+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
md=['# 綱目上表現卡與舊定位對照','','目錄：[結果](#結果)｜[待核引用範圍](#待核引用範圍)｜[完整資料](#完整資料)','','## 結果','','科甲120題與催官／貴元28題共148筆，以目前卡片重新對引用頁範圍；舊報告的現值與狀態不直接當現在狀態。','**這是E0定位對照，不是判定頁碼錯誤；舊定位也可能有問題。** 不改卡、不補卡、不從干支推神煞值，擎遊左右不自選。','','|狀態|筆數|','|---|---|']
for key,value in counts.items():md.append(f'|{key}|{value}|')
md+=['','## 待核引用範圍','','下列只列現卡引用未包含舊定位頁的候選；須回原圖判定，不因本表而自動改頁碼。','','|編號|卡片|現引用|舊定位頁|原圖|','|---|---|---|---|---|']
for r in missing:md.append(f'|{r["編號"]}|{r["卡片"]}|{json.dumps(r["目前引用"],ensure_ascii=False)}|{r["舊定位實際頁"]}|[紅框](../{r["舊原圖"].removeprefix("docs/")})|')
md+=['','## 完整資料','','[148筆現卡雜湊、來源引用及圖框坐標]('+stem+'.json)。缺卡只保留清單，31組登籍仍待使用者確認後才能補。','[CY-23撤銷摘要同步](CY23舊摘要同步-2026-11-26.md)。原圖、引用頁與字值是三件事，不拿其中一項代替全部核對。']
(D/(stem+'.md')).write_text('\n'.join(md)+'\n')
print(json.dumps({k:report[k] for k in ['上表筆數','狀態分布','引用範圍待核候選數','卡片異動']},ensure_ascii=False))
