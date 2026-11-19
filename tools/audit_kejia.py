#!/usr/bin/env python3
"""執行：科甲五題原圖、擎遊雙側及分類重算；不改卡。
目錄：layout／picture（定位）、card（現值）、main（報告與獨立比較）。
"""
import collections,json,re,shutil
from review_helpers import *
IMG=Path('/workspace/review/ocr');STEMS='甲乙丙丁戊己庚辛壬癸';BR='子丑寅卯辰巳午未申酉戌亥'
pairdoc=json.loads((D/'本輪擎遊原圖人工記錄.json').read_text());pairs=pairdoc['原圖記錄']
void=json.loads((D/'本輪科甲空亡原圖人工記錄.json').read_text())['原圖值']
age=json.loads((D/'複核人工字讀2026-11-19.json').read_text())['人工讀值']
def layout(y):
 odd=73+2*BR.index(y[1]);i=STEMS.index(y[0])//2;page=odd+(i>=2);x=[.65,.25,.85,.45,.05][i];yp=odd if i<=2 else odd+1;hx=[.95,.55,.15,.75,.35][i]
 return page,x,yp,hx

def picture(y,topic,ident):
 page,x,yp,hx=layout(y);im=Image.open(IMG/f'綱目-{page}-原圖0.png').convert('RGB');w,h=im.size
 # 一題一圖，保存年欄與科甲同組上下文；跨頁時兩個原頁分列，不重畫字。
 boxes={'空亡':(.15,.28),'擎天':(.25,.405),'遊奕':(.25,.405),'歲殿':(.34,.49),'登籍':(.34,.49)}
 ymin,ymax=boxes[topic]
 if y=='丙辰'and topic in ['擎天','遊奕']:ymin,ymax=.25,.445
 b=(max(0,int((x-.075)*w)),int(ymin*h),min(w,int((x+.075)*w)),int(ymax*h))
 cut=(max(0,int((x-.09)*w)),int(.07*h),min(w,int((x+.09)*w)),int(.54*h));tile=im.crop(cut).resize(((cut[2]-cut[0])*4,(cut[3]-cut[1])*4))
 head=Image.open(IMG/f'綱目-{yp}-原圖0.png').convert('RGB');hw,hh=head.size;hb=(max(0,int((hx-.07)*hw)),0,min(hw,int((hx+.07)*hw)),int(.15*hh));ht=head.crop(hb).resize(((hb[2]-hb[0])*4,(hb[3]-hb[1])*4))
 out=Image.new('RGB',(max(850,tile.width+ht.width+80),max(tile.height,ht.height)+95),'white');out.paste(ht,(10,85));offset=ht.width+60;out.paste(tile,(offset,85));d=ImageDraw.Draw(out)
 d.text((10,8),f'{ident} {y} {topic}；年欄p{yp}／值欄p{page}',font=FONT,fill='black');d.rectangle((10,85,10+ht.width-2,85+ht.height-2),outline='red',width=3)
 d.rectangle((offset+(b[0]-cut[0])*4,85+(b[1]-cut[1])*4,offset+(b[2]-cut[0])*4,85+(b[3]-cut[1])*4),outline='red',width=3)
 dest=PIC/'科甲欄'/(ident+'.png');out.save(dest);return str(dest.relative_to(ROOT))

def card(y,topic):
 name=f'{topic}圖列·{y}（星學綱目圖說下）.md';p=K/name
 if not p.exists():return name,None,None
 text=p.read_text();s=SOURCE.search(text);m=re.search(r'\n'+topic+r'\n\n([^\n]+)',text)
 return name,(m[1]if m else'未解析'),([int(s[2]),int(s[3]or s[2])]if s else None)

def link(path):return '../'+path.removeprefix('docs/')
def main():
 rows=[]
 for y in void:
  page,x,yp,hx=layout(y)
  for topic in ['空亡','擎天','遊奕','歲殿','登籍']:
   name,value,span=card(y,topic);ident=f'KJ-{len(rows)+1:03d}';im=picture(y,topic,ident);notes=[]
   if topic=='空亡':read='右'+void[y][0]+'／左'+void[y][1];ok=value is not None and set(value.replace('　','').replace(' ',''))==set(void[y])
   elif topic in ['歲殿','登籍']:read=age[y];ok=value==read and read!='未確認'
   else:
    pr=pairs.get(y,['待看原圖／無法判斷']*2);read=f'右{pr[0]}／左{pr[1]}（圖未分單星）';ok=False
    if y=='丙辰':read='擎天旁丑／遊奕旁未（原圖分列題名，非左右未分式）';ok=value==('丑'if topic=='擎天'else'未')
   pageok=span is not None and span[0]<=page<=span[1]
   if value is None:state='待看原圖';notes.append('缺卡，只列缺口，不補卡')
   elif not pageok:state='頁碼錯';notes.append('現引頁範圍未含實際值欄頁；不因年欄在前頁就略去續頁')
   elif ok:state='一致'
   elif '未確認'in read or '無法判斷'in read:state='待看原圖'
   elif topic in ['擎天','遊奕']and y!='丙辰':state='待看原圖';notes.append('原圖成對、未分單星；現值是否屬該組與單星配側是兩件事')
   else:state='錯欄';notes.append('原圖字與卡值不同，仍只列候選等使用者確認')
   if y in ['丁丑','己丑']and topic=='歲殿':notes.append('另有歲駕題卡；不自動將歲駕改名或等同歲殿')
   a=value or'未建卡';b=read
   q=f'請看紅框內的字，是「{a}」還是「{b}」？'
   rows.append({'編號':ident,'卡名':name,'現標頁碼':span,'年欄頁碼':yp,'原圖實際頁碼':page,'現值':value,'原圖值':read,'狀態':state,'來源類型':'人工校讀','說明':'；'.join(notes),'原圖':im,'問題':q})
 save('科甲欄全組重核.json',{'範圍':'丙丁戊己24組，每組五題；缺卡亦列，不改卡。','總數':len(rows),'狀態分布':dict(collections.Counter(x['狀態']for x in rows)),'明細':rows})
 base=json.loads((D/'擎天傳世文獻與綱目對照.json').read_text());comp=[x for x in base['比較']if not x['相同']];j={y:g for g,ys in base['張果PDF40原圖逐組'].items()for y in ys};old={x['年字']:x['綱目既有校讀']for x in base['比較']};pairrows=[];counts=collections.defaultdict(collections.Counter);others=collections.defaultdict(list)
 for x in comp:
  y=x['年字'];value=x['綱目既有校讀'];pr=pairs[y];z=x['張果40原圖'];prev=STEMS[(STEMS.index(y[0])-2)%10]+y[1]
  for mode in ['歷史定義：張果前組含對宮','原圖前組右字','同書舊卡前組值']:
   if value==BR[(BR.index(z)+6)%12]:cat='對宮線索'
   elif y[0]in'丙丁戊己'and ((mode.startswith('歷史')and prev in j and value in [j[prev],BR[(BR.index(j[prev])+6)%12]])or(mode=='原圖前組右字'and prev in pairs and value==pairs[prev][0])or(mode=='同書舊卡前組值'and value==old.get(prev))):cat='前組線索'
   else:cat='其他';others[mode].append(y)
   counts[mode][cat]+=1
  ident=f'QY-{len(pairrows)+1:02d}';pic=picture(y,'擎天',ident)
  def side(v):
   if y=='丙辰':return '擎天旁／上列'if v=='丑'else'遊奕旁／下列'if v=='未'else'不在分列原字'
   if v==pr[0]:return'右'
   if v==pr[1]:return'左'
   return'無法判斷（另側未確認）'if any('無法判斷'in c for c in pr)else'兩側皆不符'
  r=dict(x,編號=ident,原圖實際頁碼=layout(y)[0],右側字=pr[0]if y!='丙辰'else'不適用：擎天旁丑',左側字=pr[1]if y!='丙辰'else'不適用：遊奕旁未',現卡取側=side(value),張果值在側=side(z),原圖=pic,來源類型='人工校讀',問題=f'請看紅框內的字，是「右{pr[0]}、左{pr[1]}」還是「右{pr[1]}、左{pr[0]}」？',建議記法=f'擎遊一對：{pr[0]}、{pr[1]}；圖上未分單星，張果值{z}僅作他書線索。')
  if y=='丙辰':r['問題']='請看紅框內的字，是「擎天丑、遊奕未」還是「擎天未、遊奕丑」？';r['建議記法']='原圖分列「擎天丑、遊奕未」；不得套「圖上未分」模板。'
  pairrows.append(r)
 expected=['丁丑','己亥','庚寅','庚戌','庚辰','辛卯','辛未','辛酉']
 save('擎遊44筆成對原圖重核.json',{'總數':44,'分類重算':{m:dict(c)for m,c in counts.items()},'各法其他組':dict(others),'已知8組':expected,'歷史重算8組相符':set(others['歷史定義：張果前組含對宮'])==set(expected),'說明':'歷史15／21／8可重現，但21使用張果前組或其對宮；不是同書舊卡前組值。原圖前組右字法得到15／22／7，丁丑另符合前組線索。分類只說匹配模式，不判哪書正確。','明細':pairrows})
 lines=['# 科甲欄全組重核','','## 目錄','','- [範圍與注意](#範圍與注意)','- [五題逐組表](#五題逐組表)','- [擎遊44筆成對表](#擎遊44筆成對表)','- [分類獨立重算](#分類獨立重算)','- [八組特核](#八組特核)','- [需要使用者決定](#需要使用者決定)','','## 範圍與注意','','24組、五題共120筆，含缺卡行；每筆均附年欄與值欄的原圖。原圖值與頁碼分開核，不依旬次或干支偏移代填。','狀態欄只反映本輪證據；頁碼錯與字值問題可能並存，詳見說明。空亡兩字按同格字集合核對，不自行改卡內原來的左至右書寫順序。','**版式例外：丙辰欄分題印「擎天」「遊奕」，不能一律說全圖未分。** 頁73丙子年欄破損，欄名沿用使用者辨欄，不冒充完整可見原刻。','歲殿與登籍共值不等於擎天／遊奕可單邊決定；原題歲駕亦不自動改為歲殿。','','## 五題逐組表','','|編號／卡名|現標頁碼|原圖實際頁碼|現值|原圖值|狀態／說明|來源類型|紅框與問題|','|---|---|---|---|---|---|---|---|']
 for x in rows:lines.append(f'|{x["編號"]} {x["卡名"]}|{x["現標頁碼"]}|{x["原圖實際頁碼"]}（年欄{x["年欄頁碼"]}）|{x["現值"]or"缺卡"}|{x["原圖值"]}|{x["狀態"]}；{x["說明"]}|人工校讀|[圖]({link(x["原圖"])})；{x["問題"]}|')
 lines+=['','## 擎遊44筆成對表','','張果40頁值只作其他書線索，不用來補綱目缺字。原圖未分單星時，卡值落在某側不等於該側就是擎天。','','|年字／編號|原圖頁|右字|左字|現卡值／取側|張果值／在側（線索）|原圖／問題|','|---|---|---|---|---|---|---|']
 for x in pairrows:lines.append(f'|{x["年字"]} {x["編號"]}|{x["原圖實際頁碼"]}|{x["右側字"]}|{x["左側字"]}|{x["綱目既有校讀"]}／{x["現卡取側"]}|{x["張果40原圖"]}／{x["張果值在側"]}|[圖]({link(x["原圖"])})；{x["問題"]}|')
 lines+=['','## 分類獨立重算','','|比較定義|對宮線索|前組線索|其他|','|---|---|---|---|']
 for mode,c in counts.items():lines.append(f'|{mode}|{c["對宮線索"]}|{c["前組線索"]}|{c["其他"]}|')
 lines+=['','歷史定義可重現15／21／8，八組名單也相同。但若「前組值」指本輪原圖前組右字，丁丑現卯亦等於乙丑圖右卯，結果變15／22／7；若指舊卡前組值，則15／10／19。三種定義不能混稱，不能為湊21而忽略丁丑。分類不是圖字正誤裁決。','','## 八組特核','','|年字|圖頁|右／左|原圖|','|---|---|---|---|']
 for y in expected:
  x=next(r for r in pairrows if r['年字']==y);dest=PIC/'科甲欄'/('特核-'+y+'.png');shutil.copyfile(ROOT/x['原圖'],dest)
  lines.append(f'|{y}|{x["原圖實際頁碼"]}|{x["右側字"]}／{x["左側字"]}|[一組一圖]({link(str(dest.relative_to(ROOT)))})|')
 lines+=['','## 需要使用者決定','','1. 逐筆確認原圖值與頁碼；所有更改仍未套用，缺卡亦未補。','2. 擎遊未分題的原圖是否採成對記錄；丙辰分題例外應另存，不與未分式混寫。','3. 丁丑、壬戌、戊申左旁字仍待原圖裁讀；不依對宮推值。','4. 分類統計採哪個明確定義；歷史數字與原圖前組法的差異已列，不強湊。']
 (D/'科甲欄全組重核.md').write_text('\n'.join(lines)+'\n');print(json.dumps({'五題筆數':len(rows),'擎遊對數':len(pairrows),'分類':{m:dict(c)for m,c in counts.items()}},ensure_ascii=False))
if __name__=='__main__':main()
