"""執行：依使用者GM101-01讀值補錄丙辰一項；不改既有四項卡。"""
from review_helpers import *
import subprocess

def main():
 name='擎天立成圖年在未丙辰（星學綱目正傳）.md';dest=K/name;assert not dest.exists()
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in K.glob('*.md')};base=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
 text='#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第101頁：\n\n原文以圖表呈現\n\n擎天立成\n\n丙辰\n\n年在未\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n';dest.write_text(text)
 assert all(hashlib.sha256((K/n).read_bytes()).hexdigest()==h for n,h in before.items());assert len(list(K.glob('*.md')))==len(before)+1
 image='docs/待裁決/原圖/綱目99與101續核/GM101-01-年在未第4項末字.png';assert(ROOT/image).exists()
 rec={'日期':'2026-11-20','類型':'使用者確認後補錄，不覆寫舊卡','基準提交':base,'授權原話':'GM101-01這張圖是辰，繼續','確認字':'辰','對應原項':'丙辰；年在未','PDF頁碼':101,'原圖':image,'原圖SHA256':hashlib.sha256((ROOT/image).read_bytes()).hexdigest(),'新卡':name,'新卡全文':text,'既有卡張數':len(before),'既有卡內容異動':0,'既有四項卡':'擎天立成圖年在未已核四項（星學綱目正傳）.md','說明':'既有四項卡保留全文與檔名；本卡只記原先未收的第4項丙辰，不以他書丙戌覆蓋原圖。'}
 p=ROOT/'docs/勘校修訂/2026-11-20-GM101-01丙辰確認補錄.json';p.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
 with(ROOT/'docs/決定紀錄.md').open('a')as f:f.write('2026-11-20｜GM101-01年在未第4項｜使用者確認「GM101-01這張圖是辰，繼續」；依原圖記丙辰，不取外書丙戌｜只補原先未收一項，不動既有四項卡、其他年組或待裁決字。\n')
 with(ROOT/'docs/勘校修訂紀錄.md').open('a')as f:f.write('\n## 2026-11-20　【確認補錄】GM101-01丙辰\n\n使用者確認末字辰，按原圖記「丙辰／年在未」。[新增卡片與完整確認紀錄](勘校修訂/2026-11-20-GM101-01丙辰確認補錄.json)。原有19,786張卡逐檔雜湊不變，包含已核四項卡；沒有把傳世文獻的丙戌代入底本。\n')
 p=ROOT/'docs/待你處理.md';s=p.read_text();s=re.sub(r'^- GM101-01｜.*\n','',s,flags=re.M);s=s.replace('共103項（有圖100','共102項（有圖99').replace('已回填28張卡（22修訂、6新增','已回填29張卡（22修訂、7新增');p.write_text(s)
 p=ROOT/'docs/狀態.md';s=p.read_text().replace('19,786張','19,787張').replace('綱目5,222張','綱目5,223張').replace('飛廉下注截缺及101頁年在未末字已另備圖。','飛廉下注截缺已備圖；GM101-01辰已確認，另補丙辰一項，既有四項卡不變。');p.write_text(s)
 p=ROOT/'docs/來源清單.md';s=p.read_text().replace('累計5222張','累計5223張').replace('未核定未補卡|','未核定未補卡；2026-11-20使用者確認101頁GM101-01末字辰，另補丙辰一項，既有四項卡不變|');p.write_text(s)
 with(ROOT/'docs/catalog/星學綱目正傳.md').open('a')as f:f.write('\n2026-11-20｜第101頁年在未第4項GM101-01：使用者確認辰，依原圖另補丙辰一項；舊四項卡不變，合計五項分存。未以他書丙戌覆寫底本；[完整確認與新卡全文](../勘校修訂/2026-11-20-GM101-01丙辰確認補錄.json)。其餘圖頁仍待核。\n')
 save('GM101-01確認補錄驗證.json',{'日期':'2026-11-20','使用者確認':'辰','新增卡':1,'既有卡逐檔核對數':len(before),'既有卡異動':0,'總卡數':len(before)+1,'四欄齊全':all('## '+x in text for x in ['核心概念','使用規則','操作步驟','原文例子']),'首行正確':text.splitlines()[0]=='#七政四餘','出處PDF實際頁碼':101,'有原圖與確認紀錄':True,'原未四項卡未變':True,'不改其他待裁決項':True})
 print(json.dumps({'新增':1,'既有異動':0,'總卡數':len(before)+1},ensure_ascii=False))
if __name__=='__main__':main()
