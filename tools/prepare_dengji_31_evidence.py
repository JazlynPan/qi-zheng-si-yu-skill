"""執行：31組登籍覆蓋缺口的年欄、科甲欄原圖與確認入口；不建卡、不讀值。
目錄：layout（版面定位）、picture（並列原頁）、main（逐組清單與唯讀驗證）。
"""
from pathlib import Path
import json,hashlib,re,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs';K=ROOT/'qi-zheng-si-yu/knowledge';IMG=Path('/workspace/review/ocr');DEST=D/'待裁決/原圖/登籍覆蓋31組';FONT=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def layout(y):
 odd=73+2*'子丑寅卯辰巳午未申酉戌亥'.index(y[1]);i='甲乙丙丁戊己庚辛壬癸'.index(y[0])//2
 return {'年欄頁':odd if i<=2 else odd+1,'年欄中心':[.95,.55,.15,.75,.35][i],'科甲欄頁':odd if i<2 else odd+1,'科甲欄中心':[.65,.25,.85,.45,.05][i]}
def picture(y,ident,loc):
 panels=[];origins=[];header=None
 for name,pg,cx in [('年份欄',loc['年欄頁'],loc['年欄中心']),('科甲欄',loc['科甲欄頁'],loc['科甲欄中心'])]:
  src=IMG/f'綱目-{pg}-原圖0.png';im=Image.open(src).convert('RGB');w,h=im.size
  clip=(max(0,int((cx-.10)*w)),0,min(w,int((cx+.10)*w)),int(.54*h));cut=im.crop(clip);cut=cut.resize((cut.width*3,cut.height*3));panel=Image.new('RGB',(max(340,cut.width+20),cut.height+80),'white');panel.paste(cut,(10,80));dr=ImageDraw.Draw(panel);dr.text((10,7),name+f'：PDF第{pg}頁',font=FONT,fill='black');dr.text((10,34),'只標位置，不代填值',font=FONT,fill='black')
  if name=='年份欄':b=(max(0,int((cx-.065)*w)),0,min(w,int((cx+.065)*w)),int(.13*h));header=im.crop(b)
  else:b=(max(0,int((cx-.075)*w)),int(.325*h),min(w,int((cx+.075)*w)),int(.505*h))
  dr.rectangle((10+(b[0]-clip[0])*3,80+(b[1]-clip[1])*3,10+(b[2]-clip[0])*3,80+(b[3]-clip[1])*3),outline='red',width=3)
  panels.append(panel);origins.append({'原頁':pg,'區域':name,'來源檔名':src.name,'來源SHA256':sha(src),'裁切範圍':list(clip),'紅框原像素範圍':list(b)})
 out=Image.new('RGB',(sum(p.width for p in panels)+20,max(p.height for p in panels)+75),'white');dr=ImageDraw.Draw(out);dr.text((10,5),ident+' '+y+'：請先確認年組，再看登籍題字與值字',font=FONT,fill='black');dr.text((10,33),'原圖缺邊、淡損或無登籍題字時，不從歲殿值推填',font=FONT,fill='red');x=0
 for p in panels:out.paste(p,(x,75));x+=p.width+20
 dest=DEST/(ident+'-'+y+'.png');out.save(dest)
 return str(dest.relative_to(ROOT)),origins,header

def main():
 outjson=D/'檢查/登籍31組原圖待確認.json';assert not outjson.exists(),'不覆寫既有證據批次'
 snapshot={p.name:sha(p)for p in K.glob('*.md')};source=json.loads((D/'檢查/登籍覆蓋缺口31組-2026-11-20.json').read_text());years=[r['年份']for r in source['明細']['只有歲殿卡，缺登籍卡']];assert len(years)==31
 DEST.mkdir(parents=True,exist_ok=True);rows=[];heads=[]
 for i,y in enumerate(years,1):
  ident=f'DJ-{i:02d}';loc=layout(y);image,origins,head=picture(y,ident,loc);heads.append((ident,y,head))
  assert (K/f'歲殿圖列·{y}（星學綱目圖說下）.md').exists();assert not(K/f'登籍圖列·{y}（星學綱目圖說下）.md').exists()
  rows.append({'編號':ident,'年份':y,'年欄頁':loc['年欄頁'],'科甲欄頁':loc['科甲欄頁'],'是否跨頁':loc['年欄頁']!=loc['科甲欄頁'],'原圖':image,'原始圖位證據':origins,'登籍題字是否存在':'待使用者核圖確認','登籍值':'未提取；不得從歲殿卡推填','共用歲殿字值是否成立':'待逐組確認，不作全表假設','狀態':'已備原圖，未核定、未補卡','問題':f'{y}原圖是否有登籍題字；若有，其值字是什麼？','回答選項':['有登籍題字且值可讀（填字）','無登籍題字','有題字但值缺邊／淡損','看不清或年組定位有誤']})
 assert {p.name for p in K.glob('*.md')}==set(snapshot);assert all(sha(K/n)==h for n,h in snapshot.items())
 obj={'日期':'2026-11-20','來源':'星學綱目正傳原PDF內嵌圖，現有本機影像；非他書、非推值。','總組數':31,'原圖數':31,'跨頁組數':sum(r['是否跨頁']for r in rows),'卡片新增':0,'卡片修改':0,'限制':'31組只是原圖備齊，不等於已辨認31個登籍值；未讀小字、不把圈內其他星曜值配給登籍。','明細':rows}
 outjson.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 lines=['# 登籍31組逐圖待確認','','## 使用方式','','每組只有一張並列圖：左為年份欄，右為科甲欄；跨頁時各自標PDF頁碼。請先核年組，再看登籍題字與值字。','這批只備圖，不新增卡、不從歲殿推填。圖上缺邊或無登籍題字，請照實回答；圖框不是已確認字值的證據。','','|編號／年份|年欄頁／科甲欄頁|原圖|請回答|','|---|---|---|---|']
 for r in rows:lines.append(f'|{r["編號"]} {r["年份"]}|{r["年欄頁"]}／{r["科甲欄頁"]}|[年份與科甲原圖](../{r["原圖"].removeprefix("docs/")})|有登籍題字且可讀（填字）／無題字／值缺邊淡損／看不清或定位有誤|')
 lines+=['','共31組31圖，未核定、未補卡。戊寅、己丑、丙子及其他不在本31組的項目沒有重新核讀或更改。']
 (D/'檢查/登籍31組原圖待確認.md').write_text('\n'.join(lines)+'\n')
 # 只供Codex檢查年組定位；不進git、不作原字定稿。
 for start in range(0,len(heads),8):
  canvas=Image.new('RGB',(1120,780),'white');dr=ImageDraw.Draw(canvas)
  for j,(ident,y,head)in enumerate(heads[start:start+8]):
   x=(j%4)*280;yy=(j//4)*390;dr.text((x+8,yy+5),ident+' '+y,font=FONT,fill='black');w,h=head.size;scale=min(240/max(w,1),335/max(h,1));canvas.paste(head.resize((int(w*scale),int(h*scale))),(x+8,yy+40))
  canvas.save(IMG/f'登籍31年欄定位-{start//8+1}.png')
 print(json.dumps({'組數':31,'圖數':31,'跨頁組':obj['跨頁組數'],'原卡異動':0,'新增卡':0},ensure_ascii=False))
if __name__=='__main__':main()
