"""執行：河洛第2頁已裁決框核銷與T17-024原圖補錄；舊全文作完整前綴保留。
目錄：來源／補錄與雜湊／54框逐字比對／原OCR未核範圍／報告與進度。
"""
from review_helpers import *
import subprocess,shutil
from collections import Counter
DATE='2026-11-21';name='首例星盤邊欄文字（河洛五星合參案例抄本）.md';p=K/name
A=ROOT/'docs/勘校修訂/河洛2頁續核-2026-11-21';assert not A.exists();A.mkdir();folder=PIC/'河洛2頁續核-2026-11-21';folder.mkdir(exist_ok=True)
before={x.name:hashlib.sha256(x.read_bytes()).hexdigest()for x in K.glob('*.md')};old=p.read_text();base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip();assert '土虛十'not in old and '國印'not in old
src=Path('/workspace/review/ocr/河洛-2-原圖0.png');im=Image.open(src).convert('RGB');clip=(95,650,285,890);tile=im.crop(clip);rot=tile.rotate(90,expand=True);pan=Image.new('RGB',(1400,940),'white');d=ImageDraw.Draw(pan);d.text((8,8),'河洛PDF第2頁／原圖0／T17-024：土虛十、國印',font=FONT,fill='black');d.text((8,38),'左：原方向；右：逆時針90度；只旋轉縮放，不補筆畫',font=FONT,fill='red');pan.paste(tile.resize((570,720)),(10,90));pan.paste(rot.resize((720,570)),(640,90));d.rectangle((64,267,454,696),outline='red',width=4);d.rectangle((697,147,1210,537),outline='red',width=4);out=folder/'T17-024-土虛十與國印-兩方向.png';pan.save(out)
new=old+'\n《河洛五星合參案例抄本》第2頁：\n\n原文以圖表呈現\n\n土虛十\n\n國印\n\n井\n\n魁星\n\n參\n';assert new.startswith(old);p.write_bytes(new.encode());assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==v for n,v in before.items()if n!=name)
evidence={'日期':DATE,'基準提交':base,'卡片':name,'原頁':2,'原圖序號':0,'來源類型':'人工校讀','原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'原圖框位':[113,709,243,852],'上下文裁切':list(clip),'原圖':str(out.relative_to(ROOT)),'新片段':['土虛十','國印','井','魁星','參'],'處理':'僅追加原文例子；不解釋、不計算、不改舊字','舊全文':old,'新全文':new,'舊SHA256':before[name],'新SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'原有全文完整前綴':True,'其餘舊卡異動':0,'新增卡數':0,'卡片總數':len(before)};(A/'舊新全文與SHA256.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
source=json.loads((D/'T17逐條紅框對照.json').read_text())['明細'];rows=[r for r in source if r['原圖頁碼']==2];assert len(rows)==54
reading={}
for line in (D/'完整裁決-T17逐條整理-2026-11-20.md').read_text().splitlines():
 m=re.match(r'^\|(T17-\d+)\|[^|]+／2\|([^|]+)\|',line)
 if m:reading.setdefault(m[1],[]).append(m[2])
manual={'002':['關通動靜'],'004':['三台對主'],'011':['立命卯躔亢金十度'],'020':['孛壁三'],'024':['土虛十','國印'],'027':['木水刃星刃度'],'029':['日月夾官'],'033':['安身午躔柳土十四度'],'040':['辰巳午'],'049':['六害'],'053':['傷煞照命']}
for k,v in manual.items():reading['T17-'+k]=v
def compact(t):return ''.join(t.split())
card=compact(new);audit=[]
for r in rows:
 phrases=list(dict.fromkeys(reading.get(r['編號'],[])));checks=[]
 for t in phrases:
  if compact(t)in card:status='逐字命中'
  elif compact(t).replace('台','臺')in card:status='台／臺對照命中，僅檢索用，不改字'
  else:status='未命中，待核'
  checks.append({'片段':t,'結果':status})
 status='已對應現卡'if checks and all(x['結果']!='未命中，待核'for x in checks)else'待核'
 audit.append({'編號':r['編號'],'原頁':2,'原圖序號':r['原圖序號'],'原圖框位':r['原圖框位'],'原OCR候選':r['候選修訂字'],'核對片段':checks,'狀態':status,'既有紅框':r['原圖'],'本次新錄':r['編號']=='T17-024'})
summary=dict(Counter(r['狀態']for r in audit));(D/'河洛第2頁54候選框核銷-2026-11-21.json').write_text(json.dumps({'日期':DATE,'限制':'檔案逐字核對E0；本輪新看024及39框位置圖，不把54框當全頁已收完整。','統計':summary,'明細':audit},ensure_ascii=False,indent=2)+'\n')
md=['# 河洛第2頁54候選框核銷與續核','','## 範圍與結果','',f'本次追加T17-024的「土虛十」「國印」，以及39框續核的「井」「魁星」「參」，共5片段至原命例卡；新增卡0、其餘舊卡異動0，全庫{len(before):,}卡。',f'54個既有候選框的文件核對結果：{summary}。這是對照已保存裁決與現卡，不是本輪重看54張圖，也不是全頁覆蓋率。','台／臺只作查找對照，不改卡內原字。機器候選不作答案。','','## 新補原圖與完整留存','',f'[第024框兩方向紅框](../待裁決/原圖/河洛2頁續核-2026-11-21/{out.name})；[完整舊新卡與SHA256](../勘校修訂/河洛2頁續核-2026-11-21/舊新全文與SHA256.json)。','','## 逐框對照','','|編號|圖號|已收片段|結果|既有原圖|','|---|---|---|---|---|']
for r in audit:md.append(f'|{r["編號"]}|{r["原圖序號"]}|'+ '；'.join(x['片段']for x in r['核對片段'])+f'|{r["狀態"]}|[紅框]({r["既有紅框"]})|')
md+=['','## 尚未完成','', '原機器候選39段、四方向候選與54個篩選框不是同一單位，不能相減。沒有可靠OCR框的散字、紅批、環排仍須逐區人工對照。', '原圖0、1已檢視上下文；本次只對024作新定字，不宣稱其他未框字已核。下一個第一動作：原圖0上半部既有39段機器候選的框位對照，找出54框之外的字位；已定字不重問。'];(D/'河洛第2頁54候選框核銷-2026-11-21.md').write_text('\n'.join(md)+'\n')
with(ROOT/'docs/勘校修訂紀錄.md').open('a')as f:f.write('\n## 2026-11-21【原文續錄】河洛第2頁T17-024\n\n只追加「土虛十」「國印」「井」「魁星」「參」5原文片段，舊全文逐位元組完整前綴保留；不改寫原句，不外推盤面規則。[原圖及逐框核銷](檢查/河洛第2頁54候選框核銷-2026-11-21.md)；[舊新全文與SHA256](勘校修訂/河洛2頁續核-2026-11-21/舊新全文與SHA256.json)。\n')
with(ROOT/'docs/catalog/河洛五星合參案例抄本.md').open('a')as f:f.write('\n### 2026-11-21：第2頁候選框核銷與新片段\n\n第024框及39框新核土虛十、國印、井、魁星、參共5片段，僅追加到原命例卡，原全文不改；仍61卡。[54框核銷與原圖](../檢查/河洛第2頁54候選框核銷-2026-11-21.md)。54框對應不等於全頁覆蓋；圖框以外環排、紅批散字仍待核。\n')
p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
for i,line in enumerate(lines):
 if line.startswith('|河洛五星合參案例抄本|'):
  c=line.strip('|').split('|');c[6]+='；2026-11-21第2頁另核土虛十、國印、井、魁星、參5片段，只追加原命例，54候選框作文件核銷，全頁覆蓋未驗收';c[7]=DATE;lines[i]='|'+'|'.join(c)+'|'
p.write_text('\n'.join(lines)+'\n')
p=ROOT/'docs/狀態.md';s=p.read_text();s=re.sub(r'復工位置：[^\n]+','復工位置：《河洛五星合參案例抄本》第2頁T17-024已補土虛十、國印；54框已作文件核銷，未標整頁完成。下一個第一動作：原圖0上半部39段機器候選框位對照，定位54框外未收字；已定字不重讀。',s,1);p.write_text(s)
print(json.dumps({'修改卡數':1,'新增片段':5,'新增卡數':0,'全庫卡數':len(before),'54框結果':summary,'其餘舊卡異動':0},ensure_ascii=False))
