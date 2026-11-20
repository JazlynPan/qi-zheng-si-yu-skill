"""執行：記錄99頁圖註覆蓋與101頁未定字；只備圖、報告，不改卡。"""
from review_helpers import *
import shutil

def main():
 out=D/'綱目99與101頁剩餘圖註核對-2026-11-20.json';assert not out.exists()
 snapshot={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')}
 src=Path('/workspace/review/ocr/綱目-99-原圖0.png');im=Image.open(src);folder=PIC/'綱目99與101續核';folder.mkdir(parents=True,exist_ok=True)
 specs=[('天空',493,546,'天空圖注（星學綱目圖說）.md'),('天厄',440,494,'天厄圖注（星學綱目圖說）.md'),('血刃',387,441,'血刃圖注（星學綱目圖說）.md'),('勾絞',333,389,'勾絞圖注（星學綱目圖說）.md'),('白虎',279,335,'白虎圖注（星學綱目圖說）.md'),('四位喪服',64,281,'四位喪服煞星圖注（星學綱目圖說）.md')];rows=[]
 for title,x0,x1,name in specs:
  assert(K/name).exists();path=framed_image(src,[x0,631,x1,im.height-1],folder/(title+'下注.png'),'PDF第99頁 '+title+'下注：既有卡片覆蓋核對，非重新裁字',scale=4,margin=8)
  rows.append({'題名':title,'頁碼':99,'卡名':name,'原圖':path,'來源框位':[x0,631,x1,im.height-1],'狀態':'已有圖註卡，不重建；本輪只核段落覆蓋，不宣稱逐字修訂驗收'})
 missing=framed_image(src,[0,631,65,im.height-1],folder/'GM99-01-飛廉下注.png','GM99-01 PDF第99頁：飛廉下注可完整辨讀嗎？',scale=4,margin=10)
 native101=Path('/workspace/review/ocr/綱目-101-原圖0.png');yearimage=framed_image(native101,[164,549,190,583],folder/'GM101-01-年在未第4項末字.png','GM101-01 PDF第101頁：末字是辰還是戌？',scale=6,margin=28)
 ocr=[]
 for name in ['綱目99飛廉下注續核-PaddleOCRv5.json','綱目101年在未第4項續核-PaddleOCRv5.json']:
  p=Path('/workspace/review/ocr')/name;dest=ROOT/'docs/ocr/機器候選'/name;shutil.copyfile(p,dest);obj=json.loads(p.read_text());ocr.append({'檔案':str(dest.relative_to(ROOT)),'文字': [r.get('res',r).get('rec_texts',[])for r in obj['結果']]})
 issues=[{'編號':'GM99-01','題名':'飛廉下注','頁碼':99,'原圖':missing,'狀態':'原圖左緣及底部截缺，尚無可靠完整句；OCR亦為殘片，不錄卡','問題':'這段能完整辨讀嗎？','選項':'能（請照原字填寫）／不能（保留未確認）'}, {'編號':'GM101-01','題名':'年在未第4項末字','頁碼':101,'原圖':yearimage,'狀態':'人工放大保留辰／戌待核；OCR無可靠兩字讀值，不借他書代填','問題':'丙後的字是辰還是戌？','選項':'辰／戌／兩者皆非／看不清'}]
 assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')}==snapshot
 report={'日期':'2026-11-20','書名':'星學綱目正傳','來源':'原PDF內嵌PNG，僅放大裁切；未重繪原字','卡片總數':len(snapshot),'既有卡異動':0,'新增卡':0,'99頁既有圖註覆蓋段數':6,'本批待核項':2,'原圖數':8,'OCR裁切數':3,'圖註覆蓋明細':rows,'機器候選':ocr,'待核':issues,'限制':'六段已存在卡片不代表所有字形均經使用者確認；不宣稱整頁或階段1.5完成。'};save(out.name,report)
 md=['# 綱目99與101頁剩餘圖註核對','','## 本輪結果','','第99頁六段圖註已有卡片，本次只核對段落覆蓋，不重建、不改字；飛廉下注仍無法完整辨讀。','第101頁只核原先未收的年在未第4項末字；其餘已確認字列不重讀、不改卡。','原有19,786張卡逐檔雜湊一致；新卡0。這是覆蓋與原字待核紀錄，不是整頁逐字驗收。','','## 第99頁既有覆蓋','','|段落|既有卡片|原圖|','|---|---|---|']
 for x in rows:md.append(f'|{x["題名"]}|[{x["卡名"]}](../../qi-zheng-si-yu/knowledge/{x["卡名"]})|[下注原圖](../{x["原圖"].removeprefix("docs/")})|')
 md+=['','## 本機OCR與限制','']
 for x in ocr:md.append(f'- [原始機器輸出](../{x["檔案"].removeprefix("docs/")})：'+repr(x['文字'])+'；僅候選，不作原文定稿。')
 md+=['','第99頁只取飛廉下注；第101頁取第4項及上下文，沒有對第100頁暫停中的伏尸、闌干、貫索續核。','','## 待核原圖','','|編號／頁碼|問題|原圖|選項|','|---|---|---|---|']
 for x in issues:md.append(f'|{x["編號"]}／{x["頁碼"]}|{x["問題"]}|[紅框圖](../{x["原圖"].removeprefix("docs/")})|{x["選項"]}|')
 md+=['','第101頁末字不依《張果星宗》、使用者轉貼的傳世表或規律代填。飛廉下注不接用其他書的句子補尾。']
 (D/'綱目99與101頁剩餘圖註核對-2026-11-20.md').write_text('\n'.join(md)+'\n')
 p=ROOT/'docs/待你處理.md';s=p.read_text();new=[]
 for x in issues:new.append(f'- {x["編號"]}｜第{x["頁碼"]}頁{x["題名"]}：{x["問題"]}｜[報告](檢查/綱目99與101頁剩餘圖註核對-2026-11-20.md)｜[圖1]({x["原圖"].removeprefix("docs/")})｜選項：{x["選項"]}')
 s=s.replace('## 可直接回答（有圖）\n','## 可直接回答（有圖）\n\n'+'\n'.join(new)+'\n',1).replace('待處理共101項（有圖98','待處理共103項（有圖100');p.write_text(s)
 p=ROOT/'docs/狀態.md';s=p.read_text().replace('下一個第一動作：依逐頁清單續核其他未收圖註；','99頁六段既有覆蓋已核，飛廉下注截缺及101頁年在未末字已另備圖。下一個第一動作：續核73–96頁尚未逐段覆核的其餘窄欄與下表；');p.write_text(s)
 with (ROOT/'docs/catalog/星學綱目正傳.md').open('a')as f:f.write('\n2026-11-20｜圖表與待核對頁：第99頁飛廉下注、第101頁年在未第4項末字｜六段第99頁圖註已有卡，未重建；飛廉底邊截缺，101末字辰／戌仍待核，均未借他書補字；[原圖、OCR與覆蓋清單](../檢查/綱目99與101頁剩餘圖註核對-2026-11-20.md)。\n')
 print(json.dumps({k:v for k,v in report.items()if k not in ['圖註覆蓋明細','機器候選','待核']},ensure_ascii=False))
if __name__=='__main__':main()
