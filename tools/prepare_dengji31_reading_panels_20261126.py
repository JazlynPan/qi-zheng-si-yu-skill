"""執行：31組已備原圖各取年頭與登籍共值框；不讀取歲殿卡、不判字、不新增卡。"""
from review_helpers import *
from PIL import ImageChops
stem='登籍31組補卡預覽-2026-11-26';data=json.loads((D/'登籍31組原圖待確認.json').read_text());folder=PIC/stem;folder.mkdir(exist_ok=True);rows=[]
for r in data['明細']:
 tiles=[];evidence=[]
 for part in r['原始圖位證據']:
  src=Path('/workspace/review/ocr')/part['來源檔名'];assert hashlib.sha256(src.read_bytes()).hexdigest()==part['來源SHA256']
  box=part['紅框原像素範圍'];image=framed_image(src,box,folder/f'{r["編號"]}-{part["區域"]}.png',f'{r["編號"]} {part["區域"]} PDF第{part["原頁"]}頁',scale=3,margin=5)
  im=Image.open(ROOT/image);tile=im.crop((0,55,im.width,im.height));bb=ImageChops.difference(tile,Image.new('RGB',tile.size,'white')).getbbox();tile=tile.crop(bb) if bb else tile;tile.thumbnail((240,410));tiles.append(tile);evidence.append({**part,'本次紅框':image})
 out=Image.new('RGB',(550,480),'white');draw=ImageDraw.Draw(out);draw.text((4,4),f'{r["編號"]} {r["年份"]}：左年頭／右登籍共值',font=FONT,fill='black')
 for i,tile in enumerate(tiles):out.paste(tile,(i*270,45))
 dest=folder/f'{r["編號"]}-{r["年份"]}-雙框.png';out.save(dest)
 if r['編號'] in ['DJ-25','DJ-26']:
  part=r['原始圖位證據'][1];src=Path('/workspace/review/ocr')/part['來源檔名'];im=Image.open(src);box=list(part['紅框原像素範圍']);box[3]=int(im.height*.54)
  framed_image(src,box,folder/(r['編號']+'-擴至表底.png'),r['編號']+' '+r['年份']+' 科甲欄擴至表底；不靠歲殿卡推值',scale=4,margin=15)
 rows.append({**r,'本次雙框':str(dest.relative_to(ROOT)),'來源校驗':True,'本次原框':evidence,'人工讀字':'尚未填寫；不得由歲殿卡或公式產生'})
for start in range(0,len(rows),6):
 panel=Image.new('RGB',(1650,960),'white')
 for i,r in enumerate(rows[start:start+6]):panel.paste(Image.open(ROOT/r['本次雙框']),((i%3)*550,(i//3)*480))
 panel.save(Path('/workspace/review/ocr')/f'{stem}-{start+1:02d}.png')
report={'日期':'2026-11-26','明細':rows,'總組':31,'圖源校驗':31,'卡片異動':0,'限制':'本檔只準備原圖與來源；題字與值需本代理直接看圖，尚未人工判字。'}
(D/(stem+'-圖源.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'組數':31,'來源SHA一致':31,'卡片異動':0},ensure_ascii=False))
