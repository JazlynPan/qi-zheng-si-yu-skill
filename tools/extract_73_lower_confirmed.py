"""執行：照原圖可辨字補73頁下表9卡；不改既有卡、不補神煞取法。"""
from review_helpers import *
import shutil,subprocess
SPECS=[('天厄','未',[12,414,46,482]),('暴敗','未',[60,414,99,484]),('地解','未',[162,414,195,489]),('紫微','未',[194,414,229,489]),('地煞','申',[271,414,307,489]),('白虎','申',[317,414,354,489]),('大殺','申',[421,414,458,489]),('天喜','酉',[407,502,447,579]),('福星','酉',[458,502,494,579])]

def main():
 out=D/'綱目73頁下表九項續核-2026-11-20.json';assert not out.exists();before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')};base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip();src=Path('/workspace/review/ocr/綱目-73-原圖0.png');im=Image.open(src).convert('RGB');rows=[];picdir=PIC/'綱目73下表九項';picdir.mkdir(parents=True,exist_ok=True)
 for title,circle,box in SPECS:
  name=f'{title}圖列·第73頁{circle}字圈（星學綱目圖說下）.md';dest=K/name;assert not dest.exists()
  clip={'未':(0,403,270,500),'申':(270,403,530,500),'酉':(270,500,530,598)}[circle];cb={'未':(103,425,156,482),'申':(361,423,414,482),'酉':(361,516,413,573)}[circle];crop=im.crop(clip);scale=3;crop=crop.resize((crop.width*scale,crop.height*scale));pan=Image.new('RGB',(max(900,crop.width),crop.height+95),'white');pan.paste(crop,(0,95));dr=ImageDraw.Draw(pan);dr.text((8,5),'PDF第73頁 '+title+'／'+circle+'圈：只照錄圖內標示，不補取法',font=FONT,fill='black');dr.text((8,35),'紅框標示題字與圈字；相鄰未採內容不推填',font=FONT,fill='red')
  for b in [box,cb]:dr.rectangle(((b[0]-clip[0])*scale,95+(b[1]-clip[1])*scale,(b[2]-clip[0])*scale,95+(b[3]-clip[1])*scale),outline='red',width=3)
  image=picdir/(title+'-'+circle+'.png');pan.save(image)
  text='#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第73頁〈六十年甲子圖〉：\n\n原文以圖表呈現\n\n'+circle+'\n\n'+title+'\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n';assert all('## '+x in text for x in ['核心概念','使用規則','操作步驟','原文例子']);dest.write_text(text)
  rows.append({'題名':title,'圖中圈字':circle,'卡名':name,'原圖':str(image.relative_to(ROOT)),'原字框位':box,'圈字框位':list(cb),'新卡全文':text,'狀態':'原圖可辨字照錄；不補方法、年組或吉凶','校讀方式':'人工查看未申酉三格放大原圖；本機OCR僅輔助，不採地鮮、地然、能德等誤字'})
 assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items());assert len(list(K.glob('*.md')))==len(before)+9
 machine=Path('/workspace/review/ocr/綱目73下表未申酉-PaddleOCRv5.json');shutil.copyfile(machine,ROOT/'docs/ocr/機器候選'/machine.name)
 result={'日期':'2026-11-20','書名':'星學綱目正傳','PDF頁碼':73,'基準提交':base,'原圖SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'新增卡數':9,'原有卡核對數':len(before),'原有卡異動':0,'總卡數':len(before)+9,'新增空殼':0,'OCR裁切數':3,'未採':'既有龍德、飛廉、天德與年殺不重建；卷舌、咸池及其他格未作本批新增，不以原頁已跑OCR宣稱全頁完成。','明細':rows};save(out.name,result)
 md=['# 綱目73頁下表九項續核','','## 本批範圍','','新增9張：未圈4、申圈3、酉圈2。只照錄原圖圈字與題字；不解釋其代表的年組、宮位、起法或互相作用。','原有19,787張卡逐檔雜湊一致；無刪卡、改卡，沒有新增空殼。','[本機OCR候選](../ocr/機器候選/綱目73下表未申酉-PaddleOCRv5.json)共3裁切，機器誤字不入卡；人工校讀與E0檢查不等同獨立代理驗收。','','|題字／圈字|新增卡|原圖|','|---|---|---|']
 for r in rows:md.append(f'|{r["題名"]}／{r["圖中圈字"]}|[{r["卡名"]}](../../qi-zheng-si-yu/knowledge/{r["卡名"]})|[雙紅框原圖](../{r["原圖"].removeprefix("docs/")})|')
 md+=['','## 未完成範圍','','只收本批九處。第73頁其他窄欄與下表尚有未收文字；不重建既有龍德、飛廉、天德、年殺，也不把機器候選數當已核字數。登籍、擎遊等待裁決項一律未動。']
 (D/'綱目73頁下表九項續核-2026-11-20.md').write_text('\n'.join(md)+'\n')
 p=ROOT/'docs/來源清單.md';s=p.read_text().replace('累計5223張','累計5232張').replace('既有四項卡不變|','既有四項卡不變；2026-11-20第73頁下表未申酉圈可辨標示另補9卡，未標整頁完成|');p.write_text(s)
 p=ROOT/'docs/狀態.md';s=p.read_text().replace('19,787張','19,796張').replace('綱目5,223張','綱目5,232張').replace('下一個第一動作：續核73–96頁尚未逐段覆核的其餘窄欄與下表；','73頁下表未申酉圈可辨標示已另補9卡，未標整頁完成。下一個第一動作：續核73頁下表其餘未收字，再接74頁；');p.write_text(s)
 with(ROOT/'docs/catalog/星學綱目正傳.md').open('a')as f:f.write('\n2026-11-20｜第73頁下表：未圈天厄、暴敗、地解、紫微，申圈地煞、白虎、大殺，酉圈天喜、福星，可辨原字另補9卡；只照錄圈字與題字，不補取法。相鄰其餘字仍待核，不標整頁完成；[9處原圖與新增清單](../檢查/綱目73頁下表九項續核-2026-11-20.md)。\n')
 print(json.dumps({k:v for k,v in result.items()if k!='明細'},ensure_ascii=False))
if __name__=='__main__':main()
