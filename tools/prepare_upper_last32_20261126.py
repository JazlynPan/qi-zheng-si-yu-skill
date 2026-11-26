"""執行：為題名盤點剩餘32格保存原格與年頭圖；不填值、不改卡。"""
from review_helpers import *
from audit_kejia import layout
stem='綱目上表其餘32格原圖-2026-11-26';folder=PIC/stem;folder.mkdir(exist_ok=True)
matrix=json.loads((D/'綱目上表題名存在性-2026-11-26.json').read_text())
tri=json.loads((D/'綱目跨頁右緣三元36格續核-2026-11-26.json').read_text())
unread={(r['年組'],r['題名'])for r in tri['明細']if r['候選讀字']is None};ey={'乙丑','乙卯','乙巳','乙未','乙酉','乙亥'}
pending=[]
for r in matrix['明細']:
 y=r['年組'];t=r['題名']
 if r['精確檔名存在']or r['已有完整預覽']or y=='丙子'or(y,t)in unread or(t=='祿勳'and y in ey)or(t=='歲殿'and y in ['丁丑','己丑','戊午'])or t in ['擎天','遊奕']:continue
 pending.append(r)
rows=[]
for index,r in enumerate(pending,1):
 year=r['年組'];topic=r['題名'];vp,vx,hp,hx=layout(year)
 if topic in ['祿勳','官印','玉堂','文魁','文昌']:
  page=hp;x=hx;lo,hi={'祿勳':(.07,.21),'官印':(.16,.30),'玉堂':(.25,.39),'文魁':(.34,.48),'文昌':(.43,.55)}[topic]
 elif topic in ['催官','祿神','喜神','天廚','天嗣']:
  page=hp;x=hx-.1;lo,hi={'催官':(.07,.20),'祿神':(.16,.30),'喜神':(.25,.39),'天廚':(.34,.48),'天嗣':(.43,.55)}[topic]
 elif topic in ['貴元','科名']:
  x=hx-.2;page=hp
  if x<0:x+=1;page+=1
  lo,hi={'貴元':(.07,.21),'科名':(.43,.55)}[topic]
 else:assert topic=='空亡';page=vp;x=vx;lo,hi=.13,.29
 src=Path('/workspace/review/ocr')/f'綱目-{page}-原圖0.png';im=Image.open(src).convert('RGB');w,h=im.size
 box=[max(0,int((x-.08)*w)),int(lo*h),min(w,int((x+.08)*w)),min(h,int(hi*h))]
 picture=framed_image(src,box,folder/f'{index:02}-{year}-{topic}.png',f'{year} {topic} 原PDF第{page}頁：僅定位，未裁字',scale=5,margin=20)
 hs=src.with_name(f'綱目-{hp}-原圖0.png');head=Image.open(hs);hw,hh=head.size
 headpic=framed_image(hs,[max(0,int((hx-.08)*hw)),0,min(hw,int((hx+.08)*hw)),int(.16*hh)],folder/f'{index:02}-{year}-年頭.png',f'{year} 年頭 原PDF第{hp}頁',scale=4,margin=10)
 rows.append({'編號':f'UG-{index:02d}','年組':year,'題名':topic,'年頭頁':hp,'原格頁':page,'原框':box,'原圖':picture,'年頭圖':headpic,'原圖檔名':src.name,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'年頭注意':'年頭局部破損，歸組仍待確認'if year=='戊申'else'仍須看原圖，不從座標判字','讀字':'尚未填入，待人工看原圖'})
assert len(rows)==32
(D/(stem+'-圖源.json')).write_text(json.dumps({'日期':'2026-11-26','原格數':32,'卡片異動':0,'限制':'沿版式取框，只提供原格，尚不是讀字裁決。其餘81個未備全文題名中，丙子20、三元未定14、乙年祿勳右字6、擎遊6、既有歲駕2、戊午歲駕候選1均另有禁止、未定或異題記錄。','明細':rows},ensure_ascii=False,indent=2)+'\n')
for start in range(0,32,4):
 canvas=Image.new('RGB',(1400,1000),'white');d=ImageDraw.Draw(canvas)
 for i,r in enumerate(rows[start:start+4]):
  d.text((i*350+5,5),r['編號']+' '+r['年組']+' '+r['題名'],font=FONT,fill='black')
  im=Image.open(Path('/workspace/review/ocr')/r['原圖檔名']);b=r['原框'];tile=im.crop((max(0,b[0]-8),max(0,b[1]-15),min(im.width,b[2]+8),min(im.height,b[3]+15)))
  scale=min(340/tile.width,900/tile.height);tile=tile.resize((int(tile.width*scale),int(tile.height*scale)));canvas.paste(tile,(i*350,55))
 canvas.save(Path('/workspace/review/ocr')/(stem+f'-{start+1:02d}.png'))
print(json.dumps({'原格':32,'原格與年頭圖':64,'卡片異動':0},ensure_ascii=False))
