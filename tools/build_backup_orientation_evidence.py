"""執行：由既有紅框裁片產生四方向觀看圖；不重繪、補字或改卡。"""
from review_helpers import *
def main():
 folder=PIC/'完整裁決方向';folder.mkdir(parents=True,exist_ok=True);rows=[]
 for ident in ['T15-009','T15-016','T15-032','T15-074','T15-075','T17-040','T17-082']:
  src=PIC/(ident+'.png');im=Image.open(src).convert('RGB');im=im.crop((0,50,im.width,im.height));pan=Image.new('RGB',(1000,530),'white');dr=ImageDraw.Draw(pan)
  for i,angle in enumerate([0,90,180,270]):
   x=i%2*500;y=i//2*265;t=im.rotate(angle,expand=True);t.thumbnail((490,230));pan.paste(t,(x,y+30));dr.text((x+5,y),ident+' 原裁片旋轉'+str(angle)+'度',font=FONT,fill='black')
  dest=folder/(ident+'-四方向.png');pan.save(dest);rows.append({'編號':ident,'來源裁片':str(src.relative_to(ROOT)),'來源SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'方向圖':str(dest.relative_to(ROOT)),'限制':'旋轉及縮放僅助閱讀，未生成新筆畫；原字仍以原始裁片與原頁判斷'})
 save('完整裁決方向圖對照.json',{'明細':rows});print(len(rows))
if __name__=='__main__':main()
