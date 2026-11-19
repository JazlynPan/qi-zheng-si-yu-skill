"""本輪報告工具：來源定位、原圖裁切與紅框；不改卡。
目錄：pdf/pagechars（來源）、locate（字位）、word_capture（非古籍文字）。"""
import hashlib,json,re,unicodedata
from pathlib import Path
import fitz
from PIL import Image,ImageDraw,ImageFont
from opencc import OpenCC
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'qi-zheng-si-yu/knowledge';D=ROOT/'docs/檢查';PIC=ROOT/'docs/待裁決/原圖'
CC=OpenCC('s2t');FONT=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
SOURCE=re.compile(r'《([^》]+)》第\s*(\d+)(?:[—–-](\d+))?\s*(頁|段)')
LOCAL={}
for fn in ['local-manifest.json','stage15-manifest.json']:
 for r in json.loads((Path('/workspace/sources')/fn).read_text()):
  if r.get('pdf'):LOCAL[r.get('name',r.get('title'))]=Path(r['pdf'])
BOOKS={}
for line in (ROOT/'docs/來源清單.md').read_text().splitlines():
 if line.startswith('|')and'https://'in line:
  c=line.strip('|').split('|');BOOKS[c[0]]=LOCAL.get(c[1])
for a,b in {'五星玉鏡':'五星玉鏡—','增訂天官五星集腋':'增訂天官五星','袁天罡五星三命指南':'五星三命指南大全','歷學會通·元祿五星':'歷學會通：元祿五星','歷學會通·琴堂五星':'歷學會通：琴堂五星','唐·洞微歌':'唐：洞微歌'}.items():
 if b in BOOKS:BOOKS[a]=BOOKS[b]
PDFS={};CHAR={}
def pdf(book):
 path=BOOKS.get(book)
 if not path or not path.is_file():return None
 if book not in PDFS:PDFS[book]=fitz.open(path)
 return PDFS[book]
def norm(s):return ''.join(c for c in CC.convert(s).translate(str.maketrans({'爲':'為','衆':'眾','羣':'群','裏':'裡','竝':'並','囘':'回'}))if c.isalnum())
def save(name,obj):
 p=D/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');return p

def pagechars(book,pno):
 key=(book,pno)
 if key not in CHAR:
  pg=pdf(book)[pno-1];chars=[]
  for block in pg.get_text('rawdict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     for ch in span['chars']:
      for c in norm(ch['c']):chars.append((c,fitz.Rect(ch['bbox'])))
  CHAR[key]=(''.join(x[0]for x in chars),[x[1]for x in chars])
 return CHAR[key]

def framed_image(src,box,dest,label,scale=3,margin=25):
 im=Image.open(src).convert('RGB');x0,y0,x1,y1=map(int,box);cut=(max(0,x0-margin),max(0,y0-margin),min(im.width,x1+margin),min(im.height,y1+margin))
 tile=im.crop(cut);scale=min(scale,1400/max(tile.size));tile=tile.resize((max(1,int(tile.width*scale)),max(1,int(tile.height*scale))))
 panel=Image.new('RGB',(max(550,tile.width),tile.height+55),'white');panel.paste(tile,(0,55));d=ImageDraw.Draw(panel);d.text((8,10),label,font=FONT,fill='black')
 d.rectangle(((x0-cut[0])*scale,(y0-cut[1])*scale+55,(x1-cut[0])*scale,(y1-cut[1])*scale+55),outline='red',width=3)
 dest.parent.mkdir(parents=True,exist_ok=True);panel.save(dest)
 return str(dest.relative_to(D.parent.parent))

def shape(s):
 return norm(s).translate(str.maketrans({'已':'己','巳':'己','昂':'昴','末':'未','士':'土','曰':'日','牛':'午','戍':'戌','戊':'戌','甲':'申'}))

def locate(row,ident,sub='全庫形近字'):
 book=row['書名'];doc=pdf(book)
 if row['單位']=='段':return word_capture(row,ident,sub)
 if not doc:return {'定位':'待看原圖／無法判斷','原因':'非古籍來源或未取得可對應的PDF，未偽造原頁圖','原圖':None,'來源類型':'文字層'if row['單位']=='段'else'待追溯'}
 target=row['現字'];before=shape(row['前文']);after=shape(row['後文']);found=[]
 for pno in range(row['起頁'],row['迄頁']+1):
  if not 1<=pno<=len(doc):continue
  raw,boxes=pagechars(book,pno);fold=shape(raw)
  for a in range(len(raw)):
   if before and not fold[max(0,a-len(before)):a].endswith(before):continue
   if after and fold[a+1:a+1+len(after)]!=after:continue
   if not before and not after:continue
   if shape(raw[a])not in set(shape(row['候選字']+target)):continue
   found.append((pno,boxes[a],raw[a]))
 if not found and (len(before)>4 or len(after)>4):
  # 只縮短定位錨點，不據縮短結果判字；仍須唯一位置。
  b4=before[-4:];a4=after[:4]
  for pno in range(row['起頁'],min(row['迄頁'],len(doc))+1):
   raw,boxes=pagechars(book,pno);fold=shape(raw)
   for pos in range(len(raw)):
    if b4 and not fold[max(0,pos-len(b4)):pos].endswith(b4):continue
    if a4 and fold[pos+1:pos+1+len(a4)]!=a4:continue
    if shape(raw[pos])in set(shape(row['候選字']+target)):found.append((pno,boxes[pos],raw[pos]))
 if len(found)>1:
  # 同語境多處全部保留在一張圖，不任選第一處。
  panels=[]
  for pno,bb,orig in found:
   pg=doc[pno-1];cl=(bb+(-70,-25,70,25))&pg.rect;pix=pg.get_pixmap(matrix=fitz.Matrix(3,3),clip=cl);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);pan=Image.new('RGB',(600,im.height+45),'white');pan.paste(im,(0,45));dr=ImageDraw.Draw(pan);dr.text((4,4),f'{ident} {book} p{pno} 字位候選',font=FONT,fill='black');dr.rectangle(((bb.x0-cl.x0)*3,(bb.y0-cl.y0)*3+45,(bb.x1-cl.x0)*3,(bb.y1-cl.y0)*3+45),outline='red',width=3);panels.append(pan)
  result=Image.new('RGB',(600,sum(p.height for p in panels)),'white');yy=0
  for pan in panels:result.paste(pan,(0,yy));yy+=pan.height
  dest=PIC/sub/(ident+'.png');result.save(dest)
  return {'定位':'同語境多處，全部附圖；引用字位待看原圖','原圖':str(dest.relative_to(ROOT)),'來源類型':'文字層','原因':f'有{len(found)}處可能字位，不任選答案','判斷':'待看原圖'}
 if not found:
  return {'定位':'待看原圖／無法判斷','原因':'原頁文字層仍無法定位；不任選字位','原圖':None,'來源類型':'文字層'if any(pagechars(book,p)[0]for p in range(row['起頁'],min(row['迄頁'],len(doc))+1))else'OCR'}
 pno,box,original=found[0];pg=doc[pno-1];clip=box+(-65,-35,65,35);clip&=pg.rect
 pix=pg.get_pixmap(matrix=fitz.Matrix(3,3),clip=clip);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 panel=Image.new('RGB',(max(550,im.width),im.height+60),'white');panel.paste(im,(0,60));d=ImageDraw.Draw(panel);d.text((8,8),f'{ident} {book} PDF第{pno}頁',font=FONT,fill='black')
 d.rectangle(((box.x0-clip.x0)*3,(box.y0-clip.y0)*3+60,(box.x1-clip.x0)*3,(box.y1-clip.y0)*3+60),outline='red',width=3)
 dest=PIC/sub/(ident+'.png');panel.save(dest)
 return {'定位':'已依文字層語境定位；字形仍須看原圖','原圖實際頁碼':pno,'原圖':str(dest.relative_to(ROOT)),'原圖框位':list(box),'來源類型':'文字層','文字層對應字':original,'判斷':'待看原圖'}


def word_capture(row,ident,sub):
 paragraphs=json.loads(Path('/workspace/sources/楊國正講義-原始段落.json').read_text());matches=[]
 for item in paragraphs[row['起頁']-1:row['迄頁']]:
  original=item['文字'];chars=[(c,i)for i,ch in enumerate(original)for c in norm(ch)];text=''.join(c for c,i in chars);fold=shape(text);before=shape(row['前文']);after=shape(row['後文'])
  for a in range(len(text)):
   if before and not fold[max(0,a-len(before)):a].endswith(before):continue
   if after and fold[a+1:a+1+len(after)]!=after:continue
   if shape(text[a])not in shape(row['候選字']+row['現字']):continue
   matches.append((item,chars[a][1]))
 if len(matches)!=1:return {'定位':'待看原圖／無法判斷','原圖':None,'來源類型':'文字層','原因':'非古籍Word段落尚未唯一定位，沒有偽造古籍頁圖'}
 item,pos=matches[0];text=item['文字'];lo=max(0,pos-20);hi=min(len(text),pos+21);snippet=text[lo:hi];f=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',26)
 im=Image.new('RGB',(max(900,int(f.getlength(snippet))+40),160),'white');d=ImageDraw.Draw(im);d.text((12,10),f'{ident} 非古籍：Word第{item["原始段落編號"]}段文字截錄（非原頁圖）',font=FONT,fill='black');d.text((15,70),snippet,font=f,fill='black');x=15+f.getlength(text[lo:pos]);d.rectangle((x,68,x+f.getlength(text[pos]),110),outline='red',width=3)
 dest=PIC/sub/(ident+'.png');im.save(dest)
 return {'定位':'原Word段落文字截錄；無古籍原頁圖','原圖':str(dest.relative_to(ROOT)),'來源類型':'文字層','原始段落編號':item['原始段落編號'],'判斷':'待看原圖','原因':'影片字幕或講義，不能用作古籍原刻字形證據'}
