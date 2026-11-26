"""執行：八組歲殿、登籍皆缺的原圖定位；排除使用者禁止補建的丙子；不讀歲殿值、不改卡。"""
from review_helpers import *
from audit_kejia import layout
from PIL import ImageChops
stem='其餘八組歲殿登籍原圖-2026-11-26';folder=PIC/stem;folder.mkdir(exist_ok=True);years=['戊辰','癸未','壬辰','癸巳','己亥','甲辰','乙巳','戊午'];rows=[]
for i,year in enumerate(years,1):
 assert not (K/f'歲殿圖列·{year}（星學綱目圖說下）.md').exists() and not (K/f'登籍圖列·{year}（星學綱目圖說下）.md').exists()
 page,x,yp,hx=layout(year);src=Path('/workspace/review/ocr')/f'綱目-{page}-原圖0.png';head=Path('/workspace/review/ocr')/f'綱目-{yp}-原圖0.png';im=Image.open(src);hi=Image.open(head);w,h=im.size;hw,hh=hi.size
 parts=[('年頭',head,[max(0,int((hx-.075)*hw)),0,min(hw,int((hx+.075)*hw)),int(.16*hh)]),('題字與值',src,[max(0,int((x-.09)*w)),int(.32*h),min(w,int((x+.09)*w)),int(.54*h)])];tiles=[];ev=[];ident=f'DG-{i:02d}'
 for label,path,box in parts:
  image=framed_image(path,box,folder/f'{ident}-{label}.png',f'{ident} {year} {label}，原圖不補字',scale=4,margin=5);tile=Image.open(ROOT/image);tile=tile.crop((0,55,tile.width,tile.height));bb=ImageChops.difference(tile,Image.new('RGB',tile.size,'white')).getbbox();tile=tile.crop(bb) if bb else tile;tile.thumbnail((245,410));tiles.append(tile);ev.append({'區域':label,'原圖':path.name,'SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'原框':box,'紅框圖':image})
 out=Image.new('RGB',(550,480),'white');d=ImageDraw.Draw(out);d.text((5,5),f'{ident} {year} 年頭p{yp}／值欄p{page}',font=FONT,fill='black')
 for z,tile in enumerate(tiles):out.paste(tile,(z*270,50))
 dest=folder/f'{ident}-{year}-雙框.png';out.save(dest);rows.append({'編號':ident,'年份':year,'年欄頁':yp,'值欄頁':page,'原圖':str(dest.relative_to(ROOT)),'證據':ev,'讀值':'未填，待直接看圖','卡片異動':0})
for start in range(0,8,4):
 out=Image.new('RGB',(1100,960),'white')
 for z,r in enumerate(rows[start:start+4]):out.paste(Image.open(ROOT/r['原圖']),((z%2)*550,(z//2)*480))
 out.save(Path('/workspace/review/ocr')/f'{stem}-{start+1:02d}.png')
(D/(stem+'-圖源.json')).write_text(json.dumps({'日期':'2026-11-26','總組':8,'另有丙子': '使用者禁止新增，排除，不重新詢問','明細':rows,'卡片異動':0},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'待看原圖組':8,'丙子禁止新增仍排除':True,'卡片異動':0},ensure_ascii=False))
