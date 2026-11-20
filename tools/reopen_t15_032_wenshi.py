"""執行：保存使用者文室候選、334頁新紅框與待核狀態；不改卡。"""
from review_helpers import *
import subprocess

def main():
 out=D/'T15-032文星文室再核-2026-11-20.md';assert not out.exists()
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')};edits=[]
 src=Path('/workspace/review/ocr/命海-334-原頁.png');im=Image.open(src).convert('RGB');clip=(535,348,603,418);tile=im.crop(clip);scale=7;tile=tile.resize((tile.width*scale,tile.height*scale)).rotate(180,expand=True);pan=Image.new('RGB',(max(750,tile.width),tile.height+100),'white');pan.paste(tile,(0,100));dr=ImageDraw.Draw(pan);dr.text((8,7),'T15-032 PDF第334頁：文星／文室重新待核',font=FONT,fill='black');dr.text((8,38),'原頁裁切旋轉180度；不補筆畫、不依詞義選字',font=FONT,fill='black');box=(551,366,586,403);a=(clip[2]-box[2],clip[3]-box[3],clip[2]-box[0],clip[3]-box[1]);dr.rectangle((a[0]*scale,100+a[1]*scale,a[2]*scale,100+a[3]*scale),outline='red',width=3);dest=PIC/'完整裁決方向/T15-032-文室再核.png';pan.save(dest)
 lines=['# T15-032文星／文室再核','','使用者新回覆：「T15-032可能是文室」。這是候選，未視為最終採字授權。','','## 現況與原圖','','- 卡片：[命例·狀元沈懋學命](../../qi-zheng-si-yu/knowledge/命例·狀元沈懋學命（總會命海末卷兼載子平）.md)。','- 來源：《星平總會命海》PDF實際第334頁；目前卡片收文星，前次判讀不再當作無疑的原圖定字。','- 放大後，上方較像宀形覆蓋線、下方似至，較支持室；筆畫連接仍有模糊，不因文星較常見而選文星。','- 只旋轉、縮放既有原頁裁片，不畫補筆畫；原刻最後採字仍待使用者確認。','','![新增紅框放大圖](../待裁決/原圖/完整裁決方向/T15-032-文室再核.png)','','[原有裁片](../待裁決/原圖/T15-032.png)與[前次四方向圖](../待裁決/原圖/完整裁決方向/T15-032-四方向.png)保留，不覆寫。','','## 處理','','本次不改任何卡片。T15-032重新列入待核；選項文室／文星／其他字／看不清。前次完整裁決報告的四處待核是當時快照，現在另加此項為五處。']
 out.write_text('\n'.join(lines)+'\n')
 def update(p,s):
  old=p.read_text();edits.append({'檔案':str(p.relative_to(ROOT)),'舊全文':old,'新全文':s,'舊SHA256':hashlib.sha256(old.encode()).hexdigest(),'新SHA256':hashlib.sha256(s.encode()).hexdigest()});p.write_text(s)
 p=ROOT/'docs/待你處理.md';s=p.read_text();assert not re.search(r'^- T15-032｜',s,re.M);line='- T15-032｜第334頁紅框內是文室還是文星？｜[再核報告](檢查/T15-032文星文室再核-2026-11-20.md)｜[圖1](待裁決/原圖/完整裁決方向/T15-032-文室再核.png) [圖2](待裁決/原圖/T15-032.png)｜選項：文室／文星／其他字／看不清\n';s=s.replace('## 可直接回答（有圖）\n','## 可直接回答（有圖）\n\n'+line,1);g=[len(re.findall(r'^- ',v,re.M))for v in re.split(r'^## ',s,flags=re.M)[1:]];s=re.sub(r'待處理共\d+項（有圖\d+、規則\d+、等補圖\d+',f'待處理共{sum(g)}項（有圖{g[0]}、規則{g[1]}、等補圖{g[2]}',s);update(p,s)
 p=ROOT/'docs/狀態.md';s=p.read_text().replace('本輪4處字疑暫不入卡。','本輪原4處字疑暫不入卡；T15-032新增文室候選，現卡文星重新待核且未改。').replace('1. 本輪4處字疑：T15-016、T15-075、T17-040、T17-082；','1. 目前5處字疑：T15-016、T15-032、T15-075、T17-040、T17-082；');update(p,s)
 p=D/'完整裁決執行總報告-2026-11-20.md';s=p.read_text().replace('## 已完成\n','## 已完成\n\n2026-11-20後續補充：使用者提出T15-032可能為文室，現已[重新列入待核](T15-032文星文室再核-2026-11-20.md)，卡片未改。下方原四處清單為前次快照，最新共五處，不再將032文星視為已無疑的讀值。\n',1);update(p,s)
 p=ROOT/'docs/catalog/星平總會命海.md';s=p.read_text()+'\n2026-11-20｜第334頁T15-032：使用者提出文室，文星／文室重新待核；保留前次圖稿與讀值，卡片未改。[新紅框與字形比較](../檢查/T15-032文星文室再核-2026-11-20.md)。\n';update(p,s)
 p=ROOT/'docs/來源清單.md';lines=p.read_text().splitlines()
 for i,line in enumerate(lines):
  if line.startswith('|星平總會命海|'):
   c=line.strip('|').split('|');c[6]+='；2026-11-20第334頁T15-032新候選文室，現卡文星重新待核，未改卡';lines[i]='|'+'|'.join(c)+'|'
 update(p,'\n'.join(lines)+'\n')
 p=ROOT/'docs/決定紀錄.md';update(p,p.read_text()+'2026-11-20｜T15-032文室候選｜使用者說「T15-032可能是文室」；列為待核，未視為最終改字授權｜僅新增原圖與候選紀錄，現卡文星未改，前次紀錄保留。\n')
 assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')}==before
 archive=ROOT/'docs/勘校修訂/2026-11-20完整裁決/T15-032重新待核文件留存.json';archive.write_text(json.dumps({'日期':'2026-11-20','基準提交':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'原圖來源SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'原頁裁切像素':list(clip),'紅框原像素':list(box),'旋轉':180,'卡片總數':len(before),'卡片異動':0,'使用者回覆':'T15-032可能是文室','檔案舊新與SHA256':edits},ensure_ascii=False,indent=2)+'\n');print('卡片異動0，待處理入口',sum(g))
if __name__=='__main__':main()
