"""執行：依2026-11-20回填授權，補四張科名與兩處T21原字；不改既有卡。
目錄：main（原字、來源、建立、舊卡保留與確認紀錄）。
"""
import json,hashlib,subprocess,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];K=ROOT/'qi-zheng-si-yu/knowledge';D=ROOT/'docs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 snapshot={p.name:sha(p)for p in K.glob('*.md')};baseline=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();rows=[]
 for y,a,b in [('戊子',73,74),('己丑',75,76),('己卯',79,80),('己巳',83,84)]:rows.append((f'科名圖列·{y}（星學綱目圖說下）.md',f'《星學綱目正傳》第{a}–{b}頁〈六十年甲子圖〉',y+'\n\n科名\n\n土','使用者明確逐年確認科名土；原年欄與次頁值欄合列來源。'))
 rows.extend([('正廟第十一格左旁字列（星學綱目第98頁）.md','《星學綱目正傳》第98頁','正廟\n\n婁水','T21-2使用者指定婁水；只收原字，不立新術語，不解左右歸屬。'),('垣廟首格左旁上字（星學綱目第98頁）.md','《星學綱目正傳》第98頁','垣廟\n\n會','T21-3使用者指定會；左旁標記字，未定歸屬取法。')])
 records=[]
 for name,source,raw,why in rows:
  p=K/name;assert not p.exists(),name
  text='#七政四餘\n\n## 核心概念\n\n原文未提及\n\n## 使用規則\n\n'+source+'：\n\n原文以圖表呈現\n\n'+raw+'\n\n## 操作步驟\n\n原文未提及\n\n## 原文例子\n\n無\n'
  assert all(text.count('## '+f)==1 for f in ['核心概念','使用規則','操作步驟','原文例子'])
  assert not any(q.read_text()==text for q in K.glob('*.md'))
  records.append({'檔名':name,'授權與依據':why,'舊卡全文':None,'新卡全文':text,'類型':'新增補錄，沒有覆寫舊卡','新卡SHA256':hashlib.sha256(text.encode()).hexdigest()})
 target=D/'勘校修訂/2026-11-20已確認六卡補錄.json';assert not target.exists()
 target.write_text(json.dumps({'標記':'【確認補錄】','日期':'2026-11-20','基準提交':baseline,'來源':'使用者逐筆核圖＋本次要求已確認項目應實際回填卡片並保存紀錄。','新卡數':6,'既有卡片修改':0,'明細':records,'不補充':'原文未載的定義、用途、步驟不補；T21取法未定，說明留在工作紀錄，不當作原書正文。'},ensure_ascii=False,indent=2)+'\n')
 for r in records:(K/r['檔名']).write_text(r['新卡全文'])
 assert all(sha(K/n)==h for n,h in snapshot.items());assert len(list(K.glob('*.md')))==len(snapshot)+6
 p=D/'勘校修訂紀錄.md'
 with p.open('a')as f:f.write('\n## 2026-11-20　【確認補錄】四張科名與T21兩處原字\n\n科名戊子、己丑、己卯、己巳各補一張土值卡；T21-2婁水與T21-3會各補一張位置字列卡，僅原字，未定歸屬取法。六張均原先不存在，無舊全文；不把候選簊金或己巳貴元外書值混入。\n\n[六張新增完整全文與確認依據](勘校修訂/2026-11-20已確認六卡補錄.json)。本次新增6張均有實質原字；原有19,780張卡全部逐位元組不變。登籍六卡修訂在上一提交，與新增卡分開。\n')
 p=D/'決定紀錄.md'
 with p.open('a')as f:f.write('2026-11-20｜已確認新卡補錄落實｜依使用者已確認讀值及要求實際回填，新增四張科名土與T21婁水、會兩處字列卡，與修訂分開提交｜原字照錄，不補取法；簊金與己巳貴元外書參考值均未入卡。\n')
 p=D/'待裁決/科名四卡補卡清單.md';s=p.read_text().replace('本次先更正報告與記錄，不新增卡。','2026-11-20已依使用者要求全部補錄，不再停留於報告。').replace('|未建卡|','|2026-11-20已補錄|');p.write_text(s)
 p=D/'檢查/綱目98_T21本輪字形複核.md';s=p.read_text();s+='\n## 2026-11-20確認已落實入卡\n\nT21-2婁水、T21-3會已分別新增位置字列卡；不補定義或取法，仍為左旁標記字、未定歸屬取法。上文未入卡為先前狀態，現以[補錄完整全文](../勘校修訂/2026-11-20已確認六卡補錄.json)為準。T21-1簊金仍是候選，不套用。\n';p.write_text(s)
 p=D/'檢查/催官貴元抽查使用者回覆.json';data=json.loads(p.read_text())
 for r in data['明細']:
  r['套用狀態']='2026-11-20已新增科名卡'if r['題名']=='科名'else'底本未確認，不套用外書值'if r['使用者讀值']is None else'現值一致，不需修字'
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 p=D/'來源清單.md';lines=p.read_text().splitlines()
 for i,l in enumerate(lines):
  if l.startswith('|星學綱目正傳|'):
   c=l.split('|');c[-3]+='；2026-11-20已確認6張登籍修訂完成，科名四土值及98頁婁水、會原字補6卡；缺載兩卡保留舊全文，未填外書值';c[-2]='2026-11-20';lines[i]='|'.join(c)
 p.write_text('\n'.join(lines)+'\n')
 p=D/'catalog/星學綱目正傳.md';s=p.read_text();s+='\n### 2026-11-20：已確認項實際回填與補錄\n\n登籍四張改正已確認值、兩張撤除原圖無載的錯配內容並保留缺載舊檔；新補科名四張土值與T21-2婁水、T21-3會兩處原字，共6張新卡。原有全部全文在修訂紀錄留存；簊金、己巳貴元外書木／水及其他候選不套用。T21僅標記字，未定歸屬取法，不把工作說明放入原文引句。[舊／新全文](../勘校修訂/2026-11-20已確認登籍六卡.json)、[新增六卡](../勘校修訂/2026-11-20已確認六卡補錄.json)。\n';p.write_text(s)
 p=D/'狀態.md';s=p.read_text().replace('19,780','19,786').replace('綱目5,216','綱目5,222');a=s.index('復工位置：');b=s.index('\n',a);s=s[:a]+'復工位置：已確認6張登籍修訂已完成；四張科名土與T21婁水、會共6張新卡已補錄，舊全文與修訂、新增分批保存。下一個第一動作：按逐頁分界續核98頁其他左旁；簊金、己巳貴元外書值及100頁字值仍不套用。'+s[b:];s=s.replace('科名四缺卡列清單','科名四卡已依確認補錄').replace('均未入卡或補取法','其中婁水、會已補錄原字，取法仍不補');p.write_text(s)
 (D/'檢查/已確認六卡新增驗證.json').write_text(json.dumps({'日期':'2026-11-20','基準提交':baseline,'舊卡數':len(snapshot),'舊卡逐位元組異動':0,'新增6卡':list(r['檔名']for r in records),'四欄來源及標籤檢查':True,'新增空殼':0,'總卡數':len(snapshot)+6},ensure_ascii=False,indent=2)+'\n')
 print('新增6卡，原有19780張無異動；共19786張')
if __name__=='__main__':main()
