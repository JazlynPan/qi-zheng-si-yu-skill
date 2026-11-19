#!/usr/bin/env python3
"""執行：100頁整欄、已收格與原圖觀察對照；不續核貫索、不改卡。
目錄：strokes（原像素橫段輔助）、main（整欄圖與24格表）。
"""
import json,re
import numpy as np
from review_helpers import *
IMG=Path('/workspace/review/ocr/綱目-100-原圖0.png')
# 以下是本輪看整欄的暫讀，不從卡片反填；一／二及筆畫邊界不清者明列未定。
OBS={
 '伏尸':[('子','虛二','二／一，待看原圖'),('丑','女二','較支持二；待確認'),('寅','尾十四','較支持十四；待確認'),('卯','尾一','一／宿字末筆，待看原圖'),('辰','角二','二／一，待看原圖'),('巳','軫十','較支持十；待確認'),('午','星三','較支持三；待確認'),('未','柳四','較支持四；待確認'),('申','井二','二／一，待看原圖'),('酉','畢四','較支持四；待確認'),('戌','婁一','一／宿字末筆，待看原圖'),('亥','壁五','較支持五；待確認')],
 '闌干':[('午','張四','較支持四；待確認'),('未','柳三','較支持三；待確認'),('申','參四','較支持四；待確認'),('酉','畢七','折筆仍待看原圖'),('戌','奎九','折筆仍待看原圖'),('亥','室一','一／宿字末筆，待看原圖'),('子','危三','較支持三；待確認'),('丑','女二','二／一，待看原圖'),('寅','箕二','二／一，待看原圖'),('卯','尾旁未定','未收；本輪依指示暫停T22，不續判'),('辰','亢二','二／一，待看原圖'),('巳','翼十二','較支持十二；待確認')]}

def strokes(im,b):
 x0,y0,x1,y1=map(int,b);arr=np.array(im.convert('L'))[y0:y1,x0:x1];binary=arr<115;ys=[]
 for yy,line in enumerate(binary):
  longest=run=0
  for hit in line:
   run=run+1 if hit else 0;longest=max(longest,run)
  if longest>=5:ys.append(yy+y0)
 groups=[]
 for y in ys:
  if groups and y<=groups[-1][-1]+1:groups[-1].append(y)
  else:groups.append([y])
 return [round(sum(g)/len(g))for g in groups]

def main():
 im=Image.open(IMG).convert('RGB');allrows=[]
 for topic,x0,x1 in [('伏尸',263,335),('闌干',162,224)]:
  cut=(x0,0,x1,632);raw=im.crop(cut);outdir=PIC/'綱目100整欄';raw.save(outdir/(topic+'-原生整欄.png'))
  canvas=Image.new('RGB',(820,632*3+70),'white');canvas.paste(raw.resize((raw.width*3,raw.height*3)),(20,70));d=ImageDraw.Draw(canvas);d.text((10,8),'PDF100 '+topic+'：右十二支／左宿名及旁字；保留整欄',font=FONT,fill='black');d.rectangle((20,70,20+raw.width*3,70+raw.height*3-1),outline='red',width=3);canvas.save(outdir/(topic+'-整欄紅框.png'))
  name=topic+'已核並列字列（星學綱目第100頁續表）.md';text=(K/name).read_text();stored={}
  for line in text.splitlines():
   if re.fullmatch(r'[子丑寅卯辰巳午未申酉戌亥][虛女尾角軫星柳井畢婁壁張參奎室危箕亢翼][一二三四五六七八九十廿卅]*',line):stored[line[0]]=line[1:]
  for i,(branch,candidate,judgment)in enumerate(OBS[topic]):
   ident=('FS'if topic=='伏尸'else'LG')+f'-{i+1:02d}';b=(x0+6,178+39*i,x0+38,200+39*i);ys=strokes(im,b)
   panel=canvas.copy();dr=ImageDraw.Draw(panel);top=155+39*i;bottom=min(630,207+39*i);dr.rectangle((20,70+top*3,20+raw.width*3,70+bottom*3),outline='red',width=4)
   # H標記對應原像素檢出的橫段，不重畫字；可能混有宿名末筆，不能直接當數字筆畫。
   for n,y in enumerate(ys,1):
    yy=70+y*3;dr.line((20+raw.width*3+2,yy,20+raw.width*3+13,yy),fill='blue',width=1);dr.text((265,70+top*3+25*(n-1)),'H'+str(n)+f' y={y}',font=FONT,fill='blue')
   dr.text((470,70+top*3),ident+' '+branch+'格',font=FONT,fill='black');dr.text((470,70+top*3+25),f'檢出橫段 {len(ys)}（非數字定稿）',font=FONT,fill='black');dest=outdir/(ident+'.png');panel.save(dest)
   old=stored.get(branch,'未收');alt='女一'if candidate=='女二'else'柳一'if candidate=='柳四'else candidate.rstrip('一二三四五六七八九十')+({'一':'二','二':'一','三':'二','四':'一','五':'三','七':'九','九':'七','十':'十一','十四':'四十','十二':'二十'}.get(candidate[len(candidate.rstrip('一二三四五六七八九十')):],'一'))
   question=f'請看紅框內的字，是「{candidate}」還是「{alt}」？'
   if branch=='卯'and topic=='闌干':question='此格未收，本輪暫停續核；請先確認整欄對照，暫不要求讀值。'
   allrows.append({'編號':ident,'卡片':name,'圖上支字':branch,'現有已收值':old,'本輪暫讀':candidate,'判斷':judgment,'橫畫數':f'機器檢出{len(ys)}段，是否均屬數字無法判斷','橫段原像素y座標':ys,'橫段探測框':list(b),'來源類型':'人工校讀','原圖':str(dest.relative_to(ROOT)),'問題':question})
 save('綱目100整欄對照.json',{'總數':24,'已收格':sum(r['現有已收值']!='未收'for r in allrows),'未收格':sum(r['現有已收值']=='未收'for r in allrows),'原圖尺寸':list(im.size),'口徑':'只整欄對照伏尸、闌干，不再裁小格；不續核T22四格或貫索。現有已收不等於本輪驗收正確。','橫畫限制':'H只標原像素長度至少5且灰度低於115的連續橫段；可能包括宿名末筆、連筆或格線，機器橫段數不等於人工筆畫數。','明細':allrows})
 lines=['# 綱目100頁伏尸、闌干整欄對照','','## 目錄','','- [範圍與限制](#範圍與限制)','- [整欄原圖](#整欄原圖)','- [每格對照](#每格對照)','- [待看原圖與需要決定](#待看原圖與需要決定)','','## 範圍與限制','','24格：伏尸12格、闌干12格；卡片現收23格、1格未收。只對照，不改卡；不續核T22四格與貫索。來源類型人工校讀。','每筆圖仍保留整欄，紅框只指出當格，藍色H旁標指出原像素橫段位置（不畫在字上）。**橫段數不能直接當數字筆畫數**：可能混入宿名末筆或鄰筆，無法可靠分開就寫無法判斷。沒有把既收值當答案。','原PDF內嵌圖646×938像素；放大不增加真實細節。其他工具的讀值不參與原圖值判定。','','## 整欄原圖','','![伏尸整欄](../待裁決/原圖/綱目100整欄/伏尸-整欄紅框.png)','','![闌干整欄](../待裁決/原圖/綱目100整欄/闌干-整欄紅框.png)','','## 每格對照','','|編號／支格|現卡已收|本輪暫讀|橫畫數／人工判斷|整欄紅框／問題|','|---|---|---|---|---|']
 for r in allrows:lines.append(f'|{r["編號"]} {r["圖上支字"]}|{r["現有已收值"]}|{r["本輪暫讀"]}|{r["橫畫數"]}；{r["判斷"]}|[原圖](../{r["原圖"].removeprefix("docs/")})；{r["問題"]}|')
 lines+=['','## 待看原圖與需要決定','','1. 女二／女一須先分清女字末筆與旁數，不能只數看得到幾條橫線；兩處女二均未因此宣告已正確。','2. 柳四的框形輪廓較支持四，但仍須在整欄確認；不能因他工具讀一而覆寫。','3. 尾、婁、室旁的短橫是否屬數字一，或與宿字末筆黏連，仍待原圖裁決。','4. 請先確認這份整欄對照；未確認前T22四格、貫索續核保持暫停。','5. 藍色H標記只是定位輔助，不是人工筆畫定稿；不清楚者無法判斷。']
 (D/'綱目100伏尸闌干整欄對照.md').write_text('\n'.join(lines)+'\n');print('整欄2張、每格完整欄紅框24張；不改卡。')
if __name__=='__main__':main()
