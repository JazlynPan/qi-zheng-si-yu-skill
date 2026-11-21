"""執行：重建第75–82頁批次驗證與同步現況數字；不改卡片。"""
from pathlib import Path
import json,re,subprocess,hashlib
R=Path(__file__).resolve().parents[1];K=R/'qi-zheng-si-yu/knowledge';base='4b18d9724ff8713204896935fac43e976646ffc9';date='2026-11-21';j=json.loads((R/'docs/檢查/階段1.5目前覆蓋與R1檢查.json').read_text());total=j['卡片數'];r1=j['R1後目前新增卡片數'];empty=j['R1後新增空殼數']
diff=subprocess.check_output(['git','-c','core.quotePath=false','diff','--name-status',base,'HEAD','--','qi-zheng-si-yu/knowledge']).decode().splitlines();assert all(x.startswith('A\t')for x in diff);assert len(diff)==164
added=[]
for line in diff:
 p=R/line.split('\t',1)[1];t=p.read_text();assert t.startswith('#七政四餘\n');assert all(t.count('## '+x)==1 for x in ['核心概念','使用規則','操作步驟','原文例子']);added.append({'檔案':str(p.relative_to(R)),'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'日期':date,'基準提交':base,'目前提交':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'基準卡數':19831,'新增卡數':len(added),'原有卡異動':0,'卡片刪除':0,'新卡格式錯誤':0,'本批新增空殼':0,'卡片總數':total,'R1後新增卡數':r1,'目前缺載保留卡數':empty,'目前缺載保留清單':j['新增空殼'],'明細':added};(R/'docs/檢查/綱目75至82頁本批總驗證-2026-11-21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md']:
 p=R/name;s=p.read_text();s=s.replace('19,786',f'{total:,}').replace('19786',str(total)).replace('5,954',f'{r1:,}').replace('5954',str(r1));s=s.replace('其中2張舊卡','其中3張舊卡').replace('缺載保留2檔為登籍戊寅、己丑','缺載保留3檔為歲殿戊寅、登籍戊寅與登籍己丑').replace('檢查原始數字保留2','檢查原始數字保留3');s=s.replace('統計更新：2026-11-19','統計更新：2026-11-21');s=s.replace('本輪只出報告，不宣告階段1.5完成。','本輪原圖補錄與檢查已逐批保存，不宣告階段1.5完成。')
 link='檢查/' if name=='docs/階段1.5目前檢查摘要.md' else ''
 if f'{date}更新：第75–82頁下表逐批新增164卡' not in s:s+=f'\n{date}更新：第75–82頁下表逐批新增164卡，原有19,831卡未修改、刪除0；[本批總驗證]({link}綱目75至82頁本批總驗證-2026-11-21.json)。每頁仍有細字待核，下一個第一動作是第83頁下表；不標全圖或階段完成。\n'
 if '完成條件核對' in name:
  s=s.replace('保留待使用者接受。','已由使用者接受為原書結構差異，T13結案。')
  if '舊表的剩餘工作描述' not in s:s+='\n舊表的剩餘工作描述以[最新復工位置](../狀態.md)及[完整裁決執行總報告](完整裁決執行總報告-2026-11-20.md)為準；命海16頁T14已按裁決回填，不重複要求裁決。\n'
 p.write_text(s)
p=R/'docs/狀態.md';s=p.read_text();s=re.sub(r'第73–76頁已逐批補錄；第82頁本批另收15卡。[^\n]+','第75–82頁本次共新增164卡，原有19,831卡未修改；下一步第83頁下表。未明細字另記待核，不標整頁完成。',s);p.write_text(s)
print(json.dumps({k:v for k,v in report.items()if k not in ['明細','目前缺載保留清單']},ensure_ascii=False))
