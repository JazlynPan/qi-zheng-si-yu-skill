"""執行：本輪報告收尾與唯讀雜湊核驗，不改卡片。
目錄：引用頁備查、22張提報、卡數口徑、唯讀驗證。
"""
import sys,json,hashlib,re,collections
from pathlib import Path
sys.path.insert(0,'tools')
from review_helpers import *
# 無法定位的字：只交付引用頁範圍圖，明說未圈到字，不偽造字位。
p=D/'形近字批量修訂清單.json';d=json.loads(p.read_text());fallback=0
for r in d['明細']:
 if r.get('原圖'):continue
 doc=pdf(r['書名'])
 if not doc:continue
 pages=list(range(max(1,r['起頁']),min(r['迄頁'],len(doc))+1));panels=[]
 for pgno in pages:
  pg=doc[pgno-1];pix=pg.get_pixmap(matrix=fitz.Matrix(.9,.9));im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);pan=Image.new('RGB',(max(700,im.width),im.height+70),'white');pan.paste(im,(0,70));dr=ImageDraw.Draw(pan);dr.text((8,4),r['編號']+f' PDF{pgno} 引用頁；尚未定位目標字',font=FONT,fill='black');dr.text((8,30),'紅框是整頁範圍，不是字位證據；待看原圖',font=FONT,fill='red');dr.rectangle((1,71,im.width-2,pan.height-2),outline='red',width=3);panels.append(pan)
 if not panels:continue
 out=Image.new('RGB',(max(i.width for i in panels),sum(i.height for i in panels)),'white');y=0
 for im in panels:out.paste(im,(0,y));y+=im.height
 dest=PIC/'全庫形近字'/(r['編號']+'-引用頁未定位.png');out.save(dest);r['原圖']=str(dest.relative_to(ROOT));r['定位']='僅附引用頁紅框；未定位字位';r['判斷']='待看原圖';r['問題']='引用頁已附，尚未找到該字；不能據整頁框判讀A或B。';fallback+=1
stats=collections.Counter(r['定位']for r in d['明細']);d['定位分布']=dict(stats);d['按類型分布']=dict(collections.Counter(r['類型']for r in d['明細']));p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# 更新清單的42項引用頁連結，仍明列字位未定位。
p=D/'形近字批量修訂清單.md';s=p.read_text()
for r in d['明細']:
 if r['定位']=='僅附引用頁紅框；未定位字位':
  lines=s.splitlines();s='\n'.join(line.replace('未定位／沒有可用原頁圖',f'[引用頁範圍，未定位字位](../{r["原圖"].removeprefix("docs/")})')if line.startswith('|'+r['編號']+' ')else line for line in lines)+'\n'
s=s.split('\n## 按類型統計與定位限制')[0];s+='\n## 按類型統計與定位限制\n\n'+'\n'.join(f'- {k}：{v}筆。'for k,v in d['按類型分布'].items())+f'\n\n另有{fallback}筆僅附引用頁範圍框，尚未定位到目標字；不算一字一框驗收通過。Word文字截錄也不是古籍原頁圖。\n';p.write_text(s)
# 22張舊提案只列待裁決表，不改卡。
k=json.loads((D/'科甲欄全組重核.json').read_text());years={'歲殿':'丙午 丙寅 丙戌 丙申 丙辰 丁亥 丁卯 丁巳 丁未 丁酉 戊寅 戊戌 戊申 己卯 己未 己酉'.split(),'登籍':'丁丑 丁卯 丙寅 己丑 己卯 戊寅'.split()};sel=[r for r in k['明細']if any(r['卡名'].startswith(t+'圖列·'+y+'（')for t,ys in years.items()for y in ys)]
lines=['# 歲殿16張與登籍6張最終提報表','','共22張，只提報，不套用。己丑仍無法判斷；值與頁碼須分別確認。','','|卡名|現標頁|圖頁|現值|原圖讀值|紅框|','|---|---|---|---|---|---|']
for r in sel:lines.append(f'|{r["卡名"]}|{r["現標頁碼"]}|{r["原圖實際頁碼"]}|{r["現值"]}|{r["原圖值"]}|[原圖](../{r["原圖"].removeprefix("docs/")})|')
(D/'歲殿登籍22張本輪提報.md').write_text('\n'.join(lines)+'\n')
# 題目不能用「缺卡」作字形選項，也不能A與A假裝兩個候選。
p=D/'科甲欄全組重核.md';s=p.read_text();s=re.sub(r'請看紅框內的字，是「([^」]*)」還是「\1」？',r'請確認紅框內是否讀為「\1」；沒有第二個可靠字形候選，不編造選項。',s);s=re.sub(r'請看紅框內的字，是「未建卡」還是「([^」]*)」？',r'此組缺卡，只標示原圖暫讀「\1」供核對，不以缺卡作字形選項。',s);p.write_text(s)
# 卡數只更新目前報告，歷史封存不碰。
for path in [ROOT/'docs/階段1.5目前檢查摘要.md',D/'階段1.5完成條件核對-2026-11-18.md']:
 s=path.read_text().replace('19,678','19,769').replace('19679','19769').replace('5,846','5,937').replace('5847','5937');s=s.split('\n統計更新：2026-11-19')[0];s+='\n統計更新：2026-11-19；口徑為 knowledge/ 內每個 Markdown 檔計一張，共19,769張，不按來源出現次數重複計算。本輪只出報告，不宣告階段1.5完成。\n';path.write_text(s)
# 比對基準所有卡片與倫理原檔。
b=json.loads((D/'全庫複核唯讀基準.json').read_text());bad=[n for n,h in b['雜湊'].items()if not(ROOT/n).exists()or hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h];actual={str(p.relative_to(ROOT))for p in K.glob('*.md')};expected={n for n in b['雜湊']if '/knowledge/'in n};assert not bad and actual==expected,(bad,actual^expected)
h=[p for p in K.glob('*.md')if '河洛'in p.name];hs=[p for p in K.glob('*.md')if '《河洛五星合參案例抄本》'in p.read_text()];extra=[p for p in h if p not in hs]
hr=['# 河洛61張與檔名64個的統計口徑','','2026-11-19；檔名含「河洛」64個，實際引《河洛五星合參案例抄本》61張。差3張是篇名含河洛而來源是其他書；不是遺失3張。','','|檔名|實際來源|','|---|---|']
for p in extra:hr.append('|'+p.name+'|'+'；'.join(dict.fromkeys(m[1]for m in SOURCE.finditer(p.read_text())))+'|')
(D/'河洛卡數口徑說明.md').write_text('\n'.join(hr)+'\n')
save('本輪唯讀驗證.json',{'日期':'2026-11-19','卡片數':len(actual),'卡片增刪搬移':0,'受保護檔案異動':len(bad),'ETHICS受保護數':sum('ETHICS.md'in n for n in b['雜湊']),'河洛檔名數':len(h),'河洛來源卡數':len(hs),'形近字引用頁未定位':fallback,'歲殿登籍提報數':len(sel),'尚未建立說明存在':'尚未建立的檔案不代表已可用'in(ROOT/'AGENTS.md').read_text()})
print(json.dumps({'基準比對':len(actual),'異動':len(bad),'引用頁未定位':fallback,'提報22':len(sel)},ensure_ascii=False))
