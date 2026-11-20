"""執行：套用2026-11-20授權的六張登籍修訂，先存舊全文；新增卡另批。
目錄：build（限定差異）、main（備份、套用、全庫保留檢查）。
"""
import json,hashlib,re,difflib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'qi-zheng-si-yu/knowledge';D=ROOT/'docs'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();snapshot={p.name:digest(p)for p in K.glob('*.md')};records=[]
 values={'丁丑':('寅','辰'),'丙寅':('寅','辰'),'丁卯':('辰','午'),'己卯':('午','申')}
 for year in ['丁丑','丙寅','丁卯','己卯','戊寅','己丑']:
  name=f'登籍圖列·{year}（星學綱目圖說下）.md';p=K/name;old=p.read_text()
  if year in values:
   a,b=values[year];needle='\n登籍\n\n'+a+'\n';assert old.count(needle)==1
   new=old.replace(needle,'\n登籍\n\n'+b+'\n');why='使用者已確認原圖讀值；本次明確要求實際回填卡片並保存舊全文。'
   if year=='己卯':
    assert '第79頁'in new;new=new.replace('第79頁','第79–80頁');why+='原圖值欄在次頁80，保留年欄79及續頁80的跨頁定位。'
  else:
   first,last=(77,78)if year=='戊寅'else(75,76)
   assert '登籍\n\n辰'in old
   new=f'#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n《星學綱目正傳》第{first}–{last}頁〈六十年甲子圖〉：\n\n原文未提及\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
   why='使用者確認原圖沒有此年份登籍記載。撤除錯配年字／登籍題字／辰值及不適用的聯列共值註，缺載如實標示；保留既有檔案，不刪卡，不以外書午值補底本。'
  assert new!=old;records.append({'檔名':name,'修訂理由':why,'舊卡SHA256':snapshot[name],'新卡SHA256':hashlib.sha256(new.encode()).hexdigest(),'舊卡全文':old,'新卡全文':new})
 target=D/'勘校修訂/2026-11-20已確認登籍六卡.json';target.parent.mkdir(exist_ok=True)
 assert not target.exists(),'修訂備份已存在，避免覆寫舊證據'
 data={'標記':'【勘校修正】','日期':'2026-11-20','基準提交':baseline,'授權':'使用者要求前面已確認但未回填的修訂實際修改卡片，保存舊全文及勘校修訂紀錄。','修改卡數':6,'新增卡數':0,'刪除卡數':0,'不套用':'歲殿16張、T21簊金、己巳貴元外書木／水、T14未確認字、100頁字值及其他候選','明細':records}
 target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 patch=''.join(''.join(difflib.unified_diff(r['舊卡全文'].splitlines(True),r['新卡全文'].splitlines(True),fromfile='a/qi-zheng-si-yu/knowledge/'+r['檔名'],tofile='b/qi-zheng-si-yu/knowledge/'+r['檔名']))for r in records)
 target.with_suffix('.patch').write_text(patch)
 for r in records:(K/r['檔名']).write_text(r['新卡全文'])
 changed=[n for n,h in snapshot.items()if digest(K/n)!=h];assert set(changed)=={r['檔名']for r in records};assert len(list(K.glob('*.md')))==len(snapshot)
 for r in records:assert (K/r['檔名']).read_text()==r['新卡全文']
 p=D/'勘校修訂紀錄.md'
 with p.open('a')as f:f.write('\n## 2026-11-20　【勘校修正】已確認登籍六卡實際回填\n\n丁丑寅→辰、丙寅寅→辰、丁卯辰→午、己卯午→申；己卯定位改79–80頁。戊寅、己丑原圖沒有登籍記載，撤除錯配辰值、題字與不適用的聯列共值註，改為原文未提及；既有兩檔保留，不刪卡、不用外書補值。\n\n[六張修訂前後完整全文與授權](勘校修訂/2026-11-20已確認登籍六卡.json)；[限定差異](勘校修訂/2026-11-20已確認登籍六卡.patch)。其他19,774張卡內容不變；新卡另批提交。\n')
 p=D/'決定紀錄.md'
 with p.open('a')as f:f.write('2026-11-20｜已確認修訂實際回填｜使用者要求先前已確認而未改卡的項目應修改卡片，保存舊全文及【勘校修正】紀錄；本批套用6張登籍，補卡另批｜不再把確認項無限期留在報告；不套用不確定候選、外書推算或未確認字形。\n')
 p=D/'待裁決/登籍6張使用者確認.md';s=p.read_text().replace('已確認讀值，尚未套用','2026-11-20已套用');s+='\n2026-11-20已依使用者要求完成六卡回填：四張改值，兩張撤除錯配內容並如實標缺載。前段未改卡／等待授權為當時狀態，現以[本批勘校紀錄](../勘校修訂/2026-11-20已確認登籍六卡.json)為準；沒有以外書午值填補底本。\n';p.write_text(s)
 p=D/'狀態.md';s=p.read_text();a=s.index('復工位置：');b=s.index('\n',a);s=s[:a]+'復工位置：已確認登籍6卡已實際回填，舊全文與差異存勘校修訂；四張改值、兩張撤除原圖未載的錯配內容，不刪檔。下一個第一動作：另批新增四張科名土及T21婁水、會兩處已確認字形，候選與外書值不套用。'+s[b:];s=s.replace('歲殿16＋登籍6張提報、擎遊成對記法及丙辰分題例外，確認後才能修訂。','歲殿16張、擎遊成對記法及丙辰分題例外仍待確認；登籍6張已依確認修正，不能再列為未套用。');p.write_text(s)
 (D/'檢查/已確認登籍六卡回填驗證.json').write_text(json.dumps({'基準提交':baseline,'原有卡數':len(snapshot),'目前卡數':len(snapshot),'實改':changed,'實改數':6,'其他卡片內容異動':0,'新增':0,'刪除':0,'舊全文保存':True,'新全文逐檔比對':True,'缺載原檔保留':2,'外書值回填':0},ensure_ascii=False,indent=2)+'\n')
 print('六卡已修；19774張其他卡未改；舊全文、差異、驗證已保存')
if __name__=='__main__':main()
