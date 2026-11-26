"""執行：將既有195段OCR框對回原圖，產生逐框紅框與九格檢視圖；不判字、不改卡。"""
from review_helpers import *
R=ROOT;stem='河洛195段逐框覆核-2026-11-26';folder=PIC/stem;folder.mkdir(exist_ok=True)
j=json.loads((D/'階段1.5原37頁1358段文字線索-2026-11-25.json').read_text());rows=[]
for row in j['逐段']:
 if row['書名']!='河洛五星合參案例抄本':continue
 page=row['PDF實際頁碼'];index=row['框序號'];ident=f'HL{page:02d}-{index:02d}';poly=row['原框'];box=[min(p[0] for p in poly),min(p[1] for p in poly),max(p[0] for p in poly),max(p[1] for p in poly)]
 src=Path('/workspace/review/ocr')/row['原圖檔名'];im=Image.open(src);assert 0<=box[0]<box[2]<=im.width+1 and 0<=box[1]<box[3]<=im.height+1
 image=framed_image(src,box,folder/(ident+'.png'),f'{ident} 河洛PDF第{page}頁：原框，候選不當答案',scale=4,margin=12)
 rows.append({'id':ident,**row,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'紅框圖':image,'覆核狀態':'待逐框看原圖；不是OCR驗收'})
assert len(rows)==195
panels=[]
for page in [2,3,12,13,15]:
 group=[r for r in rows if r['PDF實際頁碼']==page]
 for start in range(0,len(group),9):
  out=Image.new('RGB',(1200,3*260),'white');draw=ImageDraw.Draw(out)
  for i,r in enumerate(group[start:start+9]):
   src=Image.open(R/r['紅框圖']);tile=src.crop((0,55,src.width,src.height));tile.thumbnail((390,220));x=i%3*400;y=i//3*260;out.paste(tile,(x,y+35));draw.text((x+5,y+5),r['id'],font=FONT,fill='black')
  p=Path('/workspace/review/ocr')/f'{stem}-p{page}-{start+1:02d}.png';out.save(p);panels.append({'頁':page,'起序':start+1,'檢視圖':p.name})
report={'日期':'2026-11-26','總段數':195,'範圍':'原37頁OCR批次中河洛5頁的框；不含其後原圖1及旋轉新增候選','卡片異動':0,'限制':'圖框僅回原像素定位；是否讀值正確須逐框判定。不以框數、機器同文數代替人工完成率。','九格檢視圖':panels,'明細':rows}
(D/(stem+'-原框.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'總框':len(rows),'九格檢視圖':len(panels),'卡片異動':0},ensure_ascii=False))
