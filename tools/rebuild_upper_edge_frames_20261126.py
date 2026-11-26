"""執行：由已保存的人工圖位重建乙丑、乙年右緣與丙子29圖；不判字。"""
from review_helpers import *
checks=[]
def keep(dest,render):
 old=hashlib.sha256(dest.read_bytes()).hexdigest();render();new=hashlib.sha256(dest.read_bytes()).hexdigest()
 checks.append({'圖':str(dest.relative_to(ROOT)),'重建前後相同':old==new});assert old==new
data=json.loads((D/'綱目75乙丑未見題名原格-2026-11-26.json').read_text())
src=Path('/workspace/review/ocr/綱目-75-原圖0.png');assert hashlib.sha256(src.read_bytes()).hexdigest()==data['原圖SHA256']
for r in data['明細']:
 def render(r=r):
  im=Image.open(src).convert('RGB');panel=Image.new('RGB',(1100,1320),'white');tile=im.resize((800,1170));panel.paste(tile,(0,80));draw=ImageDraw.Draw(panel)
  draw.text((5,10),f'乙丑 {r["題名"]} PDF第75頁｜原格續核，不改卡',font=FONT,fill='black');sx=800/im.width;sy=1170/im.height
  for b in [[465,0,516,65],r['原框']]:draw.rectangle((b[0]*sx,80+b[1]*sy,b[2]*sx,80+b[3]*sy),outline='red',width=3)
  panel.save(ROOT/r['原圖'])
 keep(ROOT/r['原圖'],render)
data=json.loads((D/'綱目乙年頭右緣續核-2026-11-26.json').read_text())
for r in data['祿勳待讀字']:
 def render(r=r):
  src=Path('/workspace/review/ocr')/f'綱目-{r["頁"]}-原圖0.png';assert hashlib.sha256(src.read_bytes()).hexdigest()==r['原圖SHA256'];im=Image.open(src);w,h=im.size
  framed_image(src,[int(.89*w),0,w,int(.21*h)],ROOT/r['原圖'],f'{r["年組"]}祿勳右字：字／孛／其他／看不清',scale=5,margin=15)
 keep(ROOT/r['原圖'],render)
r=data['官印完整預覽']
def official():
 src=Path('/workspace/review/ocr/綱目-95-原圖0.png');assert hashlib.sha256(src.read_bytes()).hexdigest()==r['原圖SHA256'];im=Image.open(src);w,h=im.size
 framed_image(src,[int(.89*w),0,w,int(.30*h)],ROOT/r['原圖'],'乙亥官印：左日、右計候選，不改卡',scale=5,margin=15)
keep(ROOT/r['原圖'],official)
data=json.loads((D/'綱目73丙子原欄20題讀圖-2026-11-26-圖源.json').read_text())
for r in data['明細']:
 def render(r=r):
  src=Path('/workspace/review/ocr/綱目-73-原圖0.png');assert hashlib.sha256(src.read_bytes()).hexdigest()==r['原圖SHA256']
  framed_image(src,r['原框'],ROOT/r['原圖'],f'第73頁 丙子既定欄位 {r["題名"]}｜年頭破損，不補卡',scale=5,margin=15)
 keep(ROOT/r['原圖'],render)
result={'日期':'2026-11-26','重建圖數':len(checks),'逐位元組相同':sum(r['重建前後相同']for r in checks),'卡片異動':0,'限制':'圖源與生成檔重建檢查，不是字形裁決。','明細':checks}
(D/'上表頁邊29圖重建檢查-2026-11-26.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items()if k!='明細'},ensure_ascii=False));assert len(checks)==29
