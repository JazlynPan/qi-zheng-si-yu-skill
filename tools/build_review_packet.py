#!/usr/bin/env python3
"""執行：依人工字讀與既有OCR候選產生逐筆報告、紅框原圖；不改卡、不補卡。"""
import argparse, collections, difflib, hashlib, json, math, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
P=argparse.ArgumentParser(description=__doc__)
P.add_argument('--image-dir',type=Path,required=True)
P.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
a=P.parse_args();R=a.root;I=a.image_dir;D=R/'docs/檢查';O=R/'docs/待裁決/原圖';O.mkdir(exist_ok=True,parents=True)
K=R/'qi-zheng-si-yu/knowledge';stats={}
def read(p):return json.loads(p.read_text())
def save(name,data):(D/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def norm(s):return re.sub(r'[\W_]+','',s)
def cardname(typ,y):return f'{typ}圖列·{y}（星學綱目圖說下）.md'
def value(name,typ):
 p=K/name
 if not p.exists():return '缺卡'
 m=re.search(r'\n'+re.escape(typ)+r'\n\n([^\n]+)',p.read_text());return m[1]if m else'未解析'
def markdown(name,lines):(D/name).write_text('\n'.join(lines)+'\n')
def framed(src,box,filename,label,margin=35):
 im=Image.open(src).convert('RGB');w,h=im.size;x0,y0,x1,y1=box
 x0=max(0,min(w-1,int(x0)));x1=max(x0+1,min(w,int(x1)));y0=max(0,min(h-1,int(y0)));y1=max(y0+1,min(h,int(y1)))
 cut=(max(0,x0-margin),max(0,y0-margin),min(w,x1+margin),min(h,y1+margin));tile=im.crop(cut)
 scale=min(3,900/max(tile.size));tile=tile.resize((max(1,int(tile.width*scale)),max(1,int(tile.height*scale))))
 panel=Image.new('RGB',(max(600,tile.width),tile.height+50),'white');panel.paste(tile,(0,50));draw=ImageDraw.Draw(panel)
 draw.text((8,8),label,font=FONT,fill='black');draw.rectangle(((x0-cut[0])*scale,(y0-cut[1])*scale+50,(x1-cut[0])*scale,(y1-cut[1])*scale+50),outline='red',width=4)
 panel.save(O/filename);return '../待裁決/原圖/'+filename

def yearloc(y):
 i='子丑寅卯辰巳午未申酉戌亥'.index(y[1]);start=73+2*i;cross=y[0]in'戊己';return start,start+int(cross),cross
manual=read(D/'複核人工字讀2026-11-19.json');mv=manual['人工讀值']
# 每頁一張：保留原圖上半部與欄間線，紅框只標指定年欄及聯列共值區。
page_links={}
for page in range(73,97):
 im=Image.open(I/f'綱目-{page}-原圖0.png').convert('RGB');w,h=im.size
 top=im.crop((0,0,w,int(h*.57)));scale=2;top=top.resize((top.width*scale,top.height*scale))
 panel=Image.new('RGB',(top.width,top.height+55),'white');panel.paste(top,(0,55));draw=ImageDraw.Draw(panel)
 draw.text((8,10),f'第{page}頁：紅框標年欄／共值位置；續欄見報告',font=FONT,fill='black')
 boxes=[(.49,0,.62,.14),(.09,0,.22,.14),(.18,.33,.34,.51)]if page%2 else[(.78,.32,.96,.51)]
 for j,(x0,y0,x1,y1)in enumerate(boxes):draw.rectangle((x0*w*scale,y0*h*scale+55,x1*w*scale,y1*h*scale+55),outline='red',width=4)
 fn=f'丙丁戊己-綱目{page}-年欄與科甲紅框.png';panel.save(O/fn);page_links[page]='../待裁決/原圖/'+fn
rows=[]
for typ,ys in [('歲殿',manual['歲殿指定16張']),('登籍',manual['登籍指定6張'])]:
 for y in ys:
  start,page,cross=yearloc(y);name=cardname(typ,y);old=value(name,typ)
  rows.append({'卡片':name,'現值':old,'圖上讀值':mv[y],'年欄頁碼':start,'科甲共值頁碼':page,'年欄位置':'左組'if cross else'中組','科甲位置':'下一頁最右續欄'if cross else'同頁中組左側第四欄','是否下一頁右緣':'是'if cross else'否','年欄紅框圖':page_links[start],'共值紅框圖':page_links[page],'說明':'聯列共值候選，待使用者同意才修；看不清者不推算。'})
missing=[]
for y,v in mv.items():
 start,page,cross=yearloc(y)
 absent=[typ for typ in ['歲殿','登籍']if not(K/cardname(typ,y)).exists()]
 if absent:missing.append({'年欄':y,'缺少卡類':absent,'已有歲駕卡':(K/cardname('歲駕',y)).exists(),'年欄頁碼':start,'共值頁碼':page,'圖上讀值':v,'處理':'使用者已決定只補記、不新增卡。'if y=='丙子'else'僅列補卡候選，不新增；歲駕不自動改名為歲殿。'})
save('丙丁戊己錯配逐筆複核.json',{'人工讀值證據':'複核人工字讀2026-11-19.json','指定卡數':len(rows),'明細':rows,'缺卡清單':missing,'四處獨立證據':manual['使用者獨立證據'],'不再重核':manual['不再重核'],'卡片異動數':0})
lines=['# 丙丁戊己錯配逐筆複核','','## 目錄','','- [結論](#結論)','- [指定22張](#指定22張)','- [缺卡清單](#缺卡清單)','- [四處對照與原圖檔名](#四處對照與原圖檔名)','','## 結論','','只回報，不改卡、不補卡；本表圖讀來自原圖，不用模數線索代填。22張中己丑共值褪色，標未確認。年欄依使用者四欄歸屬規則定位；原73頁丙子欄首破損，欄名依使用者獨立確認。辛巳84辰、辛亥96子已結案，不再重核。','','## 指定22張','','|卡片|現值|圖上讀值|年欄位置|科甲共值位置|下一頁右緣|原圖|','|---|---|---|---|---|---|']
for x in rows:lines.append(f'|{x["卡片"]}|{x["現值"]}|{x["圖上讀值"]}|{x["年欄頁碼"]}頁{x["年欄位置"]}|{x["科甲共值頁碼"]}頁{x["科甲位置"]}|{x["是否下一頁右緣"]}|[年欄]({x["年欄紅框圖"]})／[共值]({x["共值紅框圖"]})|')
lines+=['','## 缺卡清單','','下列逐一查檔名，不代表一律應補；依使用者規則，補卡清單與修改清單分開。丙子只補記、不新增。丁丑、己丑另有歲駕卡者不改題名。','','|年欄|缺哪些|已有歲駕|年欄頁／續欄頁|圖讀|','|---|---|---|---|---|']
for x in missing:lines.append(f'|{x["年欄"]}|{ "、".join(x["缺少卡類"])}|{x["已有歲駕卡"]}|{x["年欄頁碼"]}／{x["共值頁碼"]}|{x["圖上讀值"]}|')
lines+=['','## 四處對照與原圖檔名','','丙子73寅、戊子74辰、己卯80申、己巳84戌已納入對照，與本次局部圖讀相符。丙子不建卡；戊子兩卡只依直接決定處理，其他候選未動。','']
for page,link in page_links.items():lines.append(f'- 第{page}頁：[{Path(link).name}]({link})')
markdown('丙丁戊己錯配逐筆複核.md',lines);stats['丙丁戊己指定卡']=len(rows);stats['缺卡組']=len(missing)
# T10：候選分類，不以文字等同判定原文錯誤。
base=read(D/'擎天傳世文獻與綱目對照.json');mapping={y:g for g,ys in base['張果PDF40原圖逐組'].items()for y in ys};branches='子丑寅卯辰巳午未申酉戌亥';stems='甲乙丙丁戊己庚辛壬癸'
def opposite(v):return branches[(branches.index(v)+6)%12]if v in branches else None
cats=['擎天／游奕對宮互換','疑似跨頁錯欄','兩書實質異文','其他／未分類'];classified=[]
for row in base['比較']:
 if row['相同']:continue
 x=dict(row);y=x['年字'];prev=stems[(stems.index(y[0])-2)%10]+y[1];old=x['綱目既有校讀'];expected=x['張果40原圖']
 if old==opposite(expected):cat=cats[0];why='字值與張果同年所列的對宮相同；僅是互換候選，未證實綱目取錯星。'
 elif y[0]in'丙丁戊己' and prev in mapping and old in[mapping[prev],opposite(mapping[prev])]:cat=cats[1];why=f'字值等同前組{prev}或其對宮，疑有鄰組或續欄配對；尚未驗收。'
 else:cat=cats[3];why='尚無足夠欄位與原字證據辨別互換、錯欄或實質異文，暫不強分。'
 x.update({'類別':cat,'分類理由':why,'卡片':f'擎天圖列·{y}（星學綱目圖說下）.md','原圖頁碼':{'綱目':x['綱目頁碼'],'張果':40}});classified.append(x)
counts={c:sum(x['類別']==c for x in classified)for c in cats};assert len(classified)==44
save('T10擎天44筆四類清單.json',{'分類數':counts,'限制':'分類是候選線索，不判哪一邊錯；兩書實質異文未獨立驗證，故不強列。對宮只作比較，不改值。','明細':classified})
lines=['# T10擎天44筆四類清單','','## 目錄','']+[f'- [{c}](#{c.replace("／","")})'for c in cats]+['','本報告分類是線索，不是裁決；原圖頁碼逐筆列出。兩書實質異文需分別證實欄位與原字，不能將無法分類者硬列為異文。不同網站轉錄不算獨立版本。','']
for cat in cats:
 lines += ['## '+cat,'',f'{counts[cat]}筆。','','|年欄與卡片|綱目原頁|既有校讀|張果原頁／值|理由|','|---|---|---|---|---|']
 for x in classified:
  if x['類別']==cat:lines.append(f'|{x["卡片"]}|{x["綱目頁碼"]}|{x["綱目既有校讀"]}|40／{x["張果40原圖"]}|{x["分類理由"]}|')
markdown('T10擎天44筆四類清單.md',lines);stats['T10分類']=counts
# T14：未被最新使用者裁決涵蓋的豆包主文差異，全部保留候選，不採為原文。
records={}
for p in sorted((R/'docs/ocr/校讀').glob('星平總會命海-016*.json')):
 for x in read(p)['明細']:
  v=records.setdefault((x['原圖宮字'],x['原圖星名字']),{})
  for f in ['可確認變曜名字','可確認文字註']:
   if f in x:v[f]=x[f]
closed=set()
for p in sorted((R/'docs/ocr').glob('勘校修正-命海16*.json')):
 for x in read(p)['明細']:records[x['原圖宮字'],x['原圖星名字']][x['欄位']]=x['新值'];closed.add((x['原圖宮字'],x['原圖星名字'],x['欄位']))
closed.update([('戌','金','可確認文字註'),('亥','土','可確認文字註'),('亥','水','可確認文字註')])
suffix={'亥':'亥','午':'午','卯':'卯宮','子':'子','寅':'寅','巳':'巳宮','未':'未','辰':'辰宮','酉':'酉','戌':'戌'}
t14=[]
for row in read(D/'命海16豆包OCR主文比對.json')['明細']:
 g,s=row['宮'],row['曜']
 for f,key in [('可確認變曜名字','豆包主文曜名'),('可確認文字註','豆包主文註字')]:
  old=records[g,s][f];cand=row[key]
  if old==cand or(g,s,f)in closed:continue
  src=I/f'命海-16-{suffix[g]}局部.png';im=Image.open(src);w,h=im.size
  if s in '日月木火土金':slot=5-'日月木火土金'.index(s);box=(slot*w*.94/6,h*.16,(slot+1)*w*.94/6,h*.50)
  else:slot={'水':5,'炁':4,'孛':3,'羅':2,'計':1}[s];box=(slot*w*.94/6,h*.65,(slot+1)*w*.94/6,h)
  ix=len(t14)+1;fn=f'T14-{ix:02d}-{g}{s}.png';link=framed(src,box,fn,f'T14-{ix:02d} 命海第16頁 {g}宮{s}')
  t14.append({'編號':f'T14-{ix:02d}','卡片':f'{g}宮{s}圖列（星平總會命海）.md','原圖頁碼':16,'欄位':f,'現存讀字':old,'候選修訂字':cand,'來源':'使用者轉貼豆包OCR主文；未核定','一句話差異':f'現存「{old}」與候選「{cand}」字形或字序不同。','原圖':link,'問題':f'這一格讀成「{cand}」，而不是「{old}」，可以嗎？'})
save('T14逐條紅框對照.json',{'狀態':'候選未套用；排除已經使用者最新裁決的欄位','明細':t14})
def questions_report(name,title,rows,intro):
 lines=['# '+title,'','## 目錄','','- [範圍與限制](#範圍與限制)','- [逐條對照](#逐條對照)','','## 範圍與限制','',intro,'','## 逐條對照','']
 for x in rows:
  lines += ['### '+x['編號'],'',f'- 卡片／來源：{x["卡片"]}；PDF第{x["原圖頁碼"]}頁。',f'- 現存讀字：{x["現存讀字"]}',f'- 候選修訂字：{x["候選修訂字"]}',f'- 差異：{x["一句話差異"]}',f'- [紅框局部原圖]({x["原圖"]})',f'- 問題：**{x["問題"]}**','']
 markdown(name,lines)
questions_report('T14逐條紅框對照.md','T14命海16逐條紅框對照',t14,'只提報尚未裁決的主文差異，不改卡。候選來自豆包OCR，不當作原書定本；「叡／睿」等也只列字形差異，不因此判同義或改字。每條只問一題。原圖紅框標對應星列，欄內原有其他字保留供對照。')
stats['T14候選']=len(t14)
# T15/T17：對既有四方向OCR的每筆可定位未收錄候選附原圖；不做語義修正。
def char_cjk(c):return '\u3400'<=c<='\u9fff'
def inverse_box(box,angle,w,h,offset):
 x0,y0,x1,y1=box;pts=[]
 for x,y in[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]:
  if angle==90:x,y=w-y,x
  elif angle==180:x,y=w-x,h-y
  elif angle==270:x,y=y,h-x
  pts.append((x+offset[0],y+offset[1]))
 return[min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)]
def candidate_packet(kind,folder,cards,source_fn,source_info):
 pool={};skipped=collections.Counter()
 for p in sorted(folder.glob('*-PaddleOCRv5.json')):
  d=read(p);page=d['PDF實際頁碼'];idx=d.get('原圖序號',0);angle=d['逆時針旋轉角度'];src=source_fn(page,idx);im=Image.open(src);ow,oh=im.size
  if kind=='T15':crop=d['原頁裁切座標'];w,h=crop[2]-crop[0],crop[3]-crop[1];offset=crop[:2]
  else:w,h=ow,oh;offset=(0,0)
  names=cards[page];stored='\n'.join((K/n).read_text()for n in names if(K/n).exists());compact=norm(stored)
  for result in d['結果']:
   v=result['res']
   for text,score,box in zip(v['rec_texts'],v['rec_scores'],v['rec_boxes']):
    n=norm(text)
    if len(n)<2 or not any(char_cjk(c)for c in text) or len(n)>40 or float(score)<.35:skipped['過短／非中文字／過長／低分']+=1;continue
    # 原字與既有卡逐字相同者無須再要求使用者校一次；不靠語義判同。
    if n in compact:skipped['卡內已有逐字相同片段']+=1;continue
    b=inverse_box(box,angle,w,h,offset)
    # 命海中央圈支作盤位標籤，不與待核外環星位混同。
    if kind=='T15' and math.hypot((b[0]+b[2])/2-475,(b[1]+b[3])/2-575)<110:skipped['中央盤位標籤']+=1;continue
    key=(page,idx,n,round((b[0]+b[2])/64),round((b[1]+b[3])/64))
    item={'page':page,'idx':idx,'text':text,'score':float(score),'box':b,'src':src,'names':names}
    if key not in pool or pool[key]['score']<item['score']:pool[key]=item
 rows=[]
 for x in sorted(pool.values(),key=lambda x:(x['page'],x['idx'],x['box'][1],x['box'][0],x['text'])):
  ix=len(rows)+1;ident=f'{kind}-{ix:03d}';link=framed(x['src'],x['box'],ident+'.png',f'{ident} PDF第{x["page"]}頁 圖{x["idx"]}')
  rows.append({'編號':ident,'卡片':'、'.join(x['names']),'原圖頁碼':x['page'],'原圖序號':x['idx'],'現存讀字':'卡內無逐字相同引文；此框的人工讀值未確認。','候選修訂字':x['text']+'（機器OCR，未確認）','一句話差異':'這段機器辨識尚未與原圖核定，不代表應改成候選字。','原圖':link,'問題':f'紅框這一段讀成「{x["text"]}」可以嗎？','原圖框位':x['box'],'OCR分數':x['score']})
 info={'範圍':source_info,'狀態':'完整列出此篩選範圍內可定位OCR候選，不是原圖所有未辨字已完成切分；無可靠候選的字仍未確認。','排除筆數':dict(skipped),'每條問題數':1,'卡片異動數':0,'明細':rows};save(kind+'逐條紅框對照.json',info)
 questions_report(kind+'逐條紅框對照.md',kind+'逐條紅框對照',rows,'本清單是未校定的機器候選，不能當作原文。只列可定位、至少兩字、含中文字、分數不低於0.35且卡內無逐字相同引文者；分數只用於減少雜訊，不是正確率。相同位置、同一候選跨方向重出時保留較高分版本；不同候選各自留存。不做語義修字。\n\n每條只問是否可讀成該字串；答案也可為否，未確認前不改卡。這份清單不宣稱已把圖內所有模糊字切成單字；無可靠候選的範圍仍保持未確認。原圖不補字，只畫紅框。')
 stats[kind+'可定位未核候選']=len(rows)
cases={331:['命例·狀元翁正春命（總會命海末卷兼載子平）.md'],332:['命例·榜眼李廷機命（總會命海末卷兼載子平）.md'],333:['命例·探花鄧以贊命（總會命海末卷兼載子平）.md'],334:['命例·狀元沈懋學命（總會命海末卷兼載子平）.md'],335:['命例·榜眼吳道南命（總會命海末卷兼載子平）.md'],336:['命例·張天師命（總會命海末卷兼載子平）.md']}
candidate_packet('T15',R/'docs/ocr/機器候選/命海盤圖旋轉',cases,lambda p,i:I/f'命海-{p}-原頁.png','命海331–336頁，四方向盤圖OCR候選；已核字不自動撤銷。')
heluo={2:['首例星盤邊欄文字（河洛五星合參案例抄本）.md'],3:['首例河洛數圖中文字（河洛五星合參案例抄本）.md'],12:['次例四柱附文圖中文字（河洛五星合參案例抄本）.md'],13:['次例星盤邊欄文字（河洛五星合參案例抄本）.md'],15:['次例河洛數圖中文字（河洛五星合參案例抄本）.md']}
# 名稱依實際卡檔確認，找不到則只連同頁既有卡，不虛構檔名。
for p,names in list(heluo.items()):
 if not all((K/n).exists()for n in names):
  heluo[p]=[f.name for f in K.glob('*河洛五星合參案例抄本*.md')if f'第{p}頁' in f.read_text()]
candidate_packet('T17',R/'docs/ocr/機器候選/河洛旋轉',heluo,lambda p,i:I/f'河洛-{p}-原圖{i}.png','河洛2、3、12、13、15頁共7張原圖，四方向OCR；不解卦畫或重算。')
# T09原頁證據紅框。
t09=[]
for page,box,label in [(184,[180,1180,1370,1285],'巳宮土曜原句與原注'),(188,[620,550,950,610],'戌宮金曜原注'),(188,[180,805,1370,915],'戌宮月曜原句與原注')]:
 src=I/f'命海{page}百章歌.png';name=f'T09-{page}-{len(t09)+1}.png';t09.append({'頁碼':page,'對象':label,'原圖':framed(src,box,name,f'T09 第{page}頁 {label}')})
save('T09指定原頁核驗.json',{'日期':'2026-11-19','核驗方式':'讀原PDF文字層並查看184與188頁原圖，不以外部模型頁碼代替。','核驗':[{'頁碼':184,'原文':'原注：主人夭折。','對上':'夭折用字；此段未載天魔名。'},{'頁碼':188,'原文':'月臨戌上名天輔','對上':'天輔異文。'},{'頁碼':188,'原文':'原注：主夭害。','對上':'主夭害異文。'}],'圖證':t09})
markdown('使用者決定與T09核驗.md',['# 使用者決定與T09核驗','','- T04已改登籍戊子辰、73–74頁，舊全文與授權存勘校修訂紀錄。丙子只補記，不建卡。','- T13接受118與120差2為原書結構差異，不補兩題，結案。','- 辛巳84辰、辛亥96子：與規律不符，原圖如此。卡片不動、結案不重核。','- T09指定原PDF188頁有月天輔與金原注主夭害，已補已驗證出處；184頁巳土原注主人夭折對上，但未載天魔名，不擴張為曜名也已驗證。','']+[f'- [{x["對象"]}：PDF第{x["頁碼"]}頁]({x["原圖"]})'for x in t09]+['','第三、四項全部只製報告與候選，等待使用者確認；修改與補卡後續分開提交。'])
save('2026-11-19複核報告產出統計.json',stats);print(json.dumps(stats,ensure_ascii=False))
