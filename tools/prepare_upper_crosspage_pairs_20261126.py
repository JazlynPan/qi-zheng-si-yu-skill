"""執行：產生十二組原頁並排圖，分框天干題、中央年支與續欄；不改卡。"""
from review_helpers import *
from audit_kejia import layout
from collections import defaultdict

stem='上表十二跨頁原頁並排-2026-11-26'
data=json.loads((D/'綱目上表來源頁碼34候選-2026-11-26.json').read_text())
groups=defaultdict(list)
for r in data['明細']:groups[r['年份']].append(r)
out=PIC/stem;out.mkdir(exist_ok=True);rows=[]
for index,(year,items) in enumerate(groups.items(),1):
 page,x,yp,hx=layout(year);assert page==yp+1
 srcs=[Path('/workspace/review/ocr')/f'綱目-{n}-原圖0.png' for n in (yp,page)]
 originals=[Image.open(p).convert('RGB') for p in srcs]
 boxes=[]
 for i,im in enumerate(originals):
  w,h=im.size
  if i==0:
   rects=[(max(0,(hx-.075)*w),0,min(w,(hx+.075)*w),.12*h),(.02*w,.63*h,.59*w,.96*h)]
  else:rects=[(max(0,(x-.075)*w),.07*h,min(w,(x+.075)*w),.53*h)]
  boxes.append(rects)
 canvas=Image.new('RGB',(1400,1120),'white');draw=ImageDraw.Draw(canvas)
 draw.text((8,8),f'{year}｜前頁天干題、中央年支；次頁科甲續欄（不裁定擎遊左右）',font=FONT,fill='black')
 for i,im in enumerate(originals):
  scale=min(680/im.width,1020/im.height);tile=im.resize((int(im.width*scale),int(im.height*scale)))
  xx=5+i*700;yy=85;canvas.paste(tile,(xx,yy));draw.text((xx,48),f'PDF第{[yp,page][i]}頁原圖',font=FONT,fill='black')
  for box in boxes[i]:draw.rectangle((xx+box[0]*scale,yy+box[1]*scale,xx+box[2]*scale,yy+box[3]*scale),outline='red',width=3)
 dest=out/f'{index:02}-{year}-{yp}-{page}.png';canvas.save(dest)
 rows.append({'年份':year,'前頁':yp,'次頁續欄':page,'候選卡數':len(items),'卡片':[r['卡片'] for r in items],'原圖':str(dest.relative_to(ROOT)),
              '來源圖':[{'檔名':p.name,'SHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'框':boxes[i]}for i,p in enumerate(srcs)],
              '限制':'座標沿用版式定位，只提供前頁與次頁原像素並排；須人工看圖，不能由此自動判值或套用頁碼。'})
assert len(rows)==12 and sum(r['候選卡數']for r in rows)==34
(D/(stem+'-圖源.json')).write_text(json.dumps({'日期':'2026-11-26','組數':12,'涉及卡數':34,'卡片異動':0,'明細':rows},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'並排圖':12,'涉及候選卡':34,'卡片異動':0},ensure_ascii=False))
