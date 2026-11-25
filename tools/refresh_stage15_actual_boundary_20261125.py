"""執行：依本輪逐頁原圖報告更新復工分界；不修改卡片、不宣告驗收。"""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1];D=R/'docs/檢查'
p=D/'階段1.5待校與待裁決分界.json';j=json.loads(p.read_text());j['日期']='2026-11-25';j['卡片數']=len(list((R/'qi-zheng-si-yu/knowledge').glob('*.md')))
plans=[]
for p in D.glob('綱目*細字續核-2026-11-25-人工定字稿.json'):
 plan=json.loads(p.read_text());plans.append(plan)
central='綱目十二歲駕字區與命海132格覆蓋-2026-11-25.md'
for row in j['明細']:
 book=row['書名'];n=row['頁碼'];updates=[];remaining=[];links=[]
 if book=='星學綱目正傳':
  for plan in plans:
   items=[x for x in plan['明細'] if x['頁']==n]
   if items:
    updates.extend(x.get('原文字列',x['題字']) for x in items);links.append(plan['批名']+'.md')
    remaining.extend(t for t in plan['保留待核'] if t.startswith(str(n)+'頁'))
  if n in range(73,97,2):
   updates.append('中央歲駕字區與原卡已對上，不再籠統列作待補卡');links.append(central)
   remaining=[re.sub(r'(與)?中央歲駕(其他)?細註(仍)?(保留|未全核|尚有未核|未核)?','',x) for x in remaining]
  if n==84:
   updates.append('伏尸旁軫九經擴框已續錄');links.append('綱目84頁伏尸旁字再核-2026-11-25.md');remaining=[x for x in remaining if '伏尸旁' not in x]+['飛廉下注邊損字仍保留，不由別頁補字。']
  if n==97:
   updates=['天嗣下注及表頭横看、前有總圖合地支看原文已補'];remaining=['玉堂首格未／木仍待確認；其他細點不自行補字。'];links=['綱目97天嗣下注續核-2026-11-25.md','綱目97表頭讀圖註續錄-2026-11-25.md']
  if n==98:
   updates=['簊金、婁水、會已按使用者確認收錄；三欄下注本輪已續錄'];remaining=['其他左旁細字與字位仍不全清，不由下注補取法。'];links=['綱目98三欄下注續核-2026-11-25.md']
  if n==99:
   updates=['飛廉下注可辨原文已新增卡，不再寫成未補錄'];remaining=['原圖其他細字與列末仍未全數逐字驗收。'];links=['綱目99飛廉下注續核-2026-11-25.md']
  if n==41:
   updates=['七八月可辨字已收；九至十二月四張原圖已再核'];remaining=['圈支淡損，無法可靠逐格配對，等GM41-09至12裁決。'];links=['綱目41九至十二月圈支續核-2026-11-25.md']
  if 73<=n<=96:
   remaining.append('上表擎遊取左右與缺登籍等仍依原待決清單；未核整頁細字不以本次局部結果代替。')
 elif book=='星平總會命海':
  if n==16:
   updates=['T14已裁決字不重問；132個宮曜位置都有具名卡，缺具名卡0'];remaining=['132格存在性為E0，不等於每字讀值全部驗收。'];links=[central]
  else:
   updates=['本輪已查看原生圖與分區放大圖；原生圖僅410–416像素寬'];remaining=['T15-016、032、075及圖糊022／024等依原範圍保留；不由OCR候選、他書或名家命盤推字。'];links=['命海六盤原生解析度續核-2026-11-25.md']
 elif book=='河洛五星合參案例抄本':
  if n==3:
   updates=['原圖39個OCR框已分區對照，數字、卦畫、紅筆符號不另造規則卡'];remaining=['符號取法原書未展開，不補推；圖糊處保留。'];links=['河洛第3頁39框分區覆核-2026-11-25.md']
  if n in [12,15]:
   updates=['本輪已補可讀運程及天元原文，原有字不改'];remaining=['第12頁T17-082末字仍待核。' if n==12 else '候卦未濟／未逢待HL15-候卦裁決；不覆寫原卡。'];links=['河洛12與15頁續核-2026-11-25.md']
  if n==2:
   updates=['T17-040辰巳午與052火迫金龍等已收，另有本輪分區續核報告'];remaining=['紅筆符號與淡損部分不當作已知規則；不重建已收片段。'];links=['河洛第2頁分區覆核-2026-11-21.md']
   if not (D/links[0]).exists():links=[]
  if n==13:
   updates=['兩張原生圖本輪皆已查看；邊欄可辨字已見既有命例卡'];remaining=['T17-119依指示保留圖糊；細淡字與紅筆符號不猜測。'];links=[]
 if updates:row['目前已處理']='；'.join(updates)
 if remaining:row['未完成範圍']='；'.join(remaining)
 if links:row['最新報告']=list(dict.fromkeys(links))
 row['下一動作']='只處理未完成範圍；已收原文不重建。尚待使用者決定的字值或補卡，未授權不套用。'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
md=['# 階段1.5待校與待裁決分界','','## 統計口徑','','2026-11-25：knowledge每個Markdown檔計一張，共20,340張。30份來源為29本PDF共3,430頁及1份Word253段；27份所列正文完成、3份圖像與疑字仍進行中。','列記43個圖頁位置不是43頁未讀。原37頁1,358段是OCR候選，不是概念數、缺卡數或已驗收數。','本表不把重看原圖、E0存在性檢查或局部補錄，說成全頁完成。','','## 逐頁範圍','','|書名／PDF頁|本輪已處理|實際保留範圍|最新報告|','|---|---|---|---|']
for row in j['明細']:
 links=row.get('最新報告',[]);link='、'.join(f'[報告{i+1}]({f})' for i,f in enumerate(links)) or '見逐書catalog與原逐頁紀錄'
 md.append(f'|{row["書名"]} {row["頁碼"]}|{row.get("目前已處理","原逐頁可辨字已收，本輪未新增確定字")}|{row["未完成範圍"]}|{link}|')
md+=['','## 接續位置','','先按逐頁未完成欄核銷剩餘細字，原圖仍看不清的列待核；不得把已收的拔鞍、黃旛、陌越及各頁宿旁明字重新列作未收。','尚未得到完整逐框驗收結果前，不把1,358個OCR框全部標完成，也不只留下使用者待決而隱去仍需核對的範圍。','雲端30份原檔已於2026-11-25重新串流核對SHA256，三方相符30/30；期間新增0份。[雲端證據](雲端與本輪全文複核-2026-11-25.md)。','[逐頁完整資料](階段1.5待校與待裁決分界.json)。階段1.5維持進行中，不進階段2。']
(D/'階段1.5待校與待裁決分界.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'列記頁':len(j['明細']),'已更新具體處理範圍':sum('目前已處理'in x for x in j['明細']),'卡片數':j['卡片數']},ensure_ascii=False))
