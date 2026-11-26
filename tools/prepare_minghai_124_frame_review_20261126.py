"""執行：依PDF原圖物件與文字層幾何位置分流124個OCR框，不判定OCR字值。"""
from review_helpers import *
from collections import Counter
stem='命海124框來源與覆核-2026-11-26';folder=PIC/stem;folder.mkdir(exist_ok=True)
j=json.loads((D/'階段1.5原37頁1358段文字線索-2026-11-25.json').read_text());doc=pdf('星平總會命海');rows=[]
for row in j['逐段']:
 if row['書名']!='星平總會命海':continue
 n=row['PDF實際頁碼'];index=row['框序號'];src=Path('/workspace/review/ocr')/row['原圖檔名'];im=Image.open(src);pg=doc[n-1];sx=im.width/pg.rect.width;sy=im.height/pg.rect.height;assert abs(sx-sy)<.002
 poly=row['原框'];bbox=[min(p[0]for p in poly),min(p[1]for p in poly),max(p[0]for p in poly),max(p[1]for p in poly)];box=fitz.Rect(bbox);assert box.get_area()>0
 image_rects=[fitz.Rect(rect.x0*sx,rect.y0*sy,rect.x1*sx,rect.y1*sy) for x in pg.get_images(full=True) for rect in pg.get_image_rects(x[0])]
 overlap=max(((box&b).get_area()/box.get_area() for b in image_rects),default=0)
 clip=fitz.Rect(box.x0/sx,box.y0/sy,box.x1/sx,box.y1/sy);native=pg.get_text('text',clip=clip).strip()
 kind='盤圖內候選，需看原圖' if overlap>=.8 else ('文字層範圍，原句另核' if overlap<=.05 and native else '邊界或未定位，需看原圖')
 ident=f'MH{n}-{index:02d}';image=framed_image(src,bbox,folder/(ident+'.png'),f'{ident} PDF第{n}頁：原框；候選不是答案',scale=3,margin=8)
 rows.append({'id':ident,**row,'PDF圖像覆蓋比':round(overlap,5),'來源分流':kind,'原PDF文字層截取':native,'紅框圖':image,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'限制':'來源分流只依幾何位置，不代表文字正確或內容已提煉'})
assert len(rows)==124
panels=[]
for n in range(331,337):
 group=[r for r in rows if r['PDF實際頁碼']==n and r['來源分流']!='文字層範圍，原句另核']
 for start in range(0,len(group),9):
  out=Image.new('RGB',(1200,780),'white');draw=ImageDraw.Draw(out)
  for i,r in enumerate(group[start:start+9]):
   im=Image.open(ROOT/r['紅框圖']);tile=im.crop((0,55,im.width,im.height));tile.thumbnail((390,220));x=i%3*400;y=i//3*260;out.paste(tile,(x,y+35));draw.text((x+4,y+4),r['id'],font=FONT,fill='black')
  target=Path('/workspace/review/ocr')/f'{stem}-p{n}-{start+1:02d}.png';out.save(target);panels.append(target.name)
result={'日期':'2026-11-26','總框數':124,'來源分流':dict(Counter(x['來源分流'] for x in rows)),'來源分流證據等級':'E0，PDF物件與像素座標；不是原圖核字驗收','圖內檢視圖':panels,'明細':rows}
(D/(stem+'-來源分流.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='明細'},ensure_ascii=False))
