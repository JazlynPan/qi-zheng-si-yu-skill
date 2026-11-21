"""執行：核對87–88頁批次、同步目前摘要數字；不改知識卡。"""
from pathlib import Path
import json,re,subprocess,hashlib
R=Path(__file__).resolve().parents[1];base='fecce54c75bb13bf55aec40244fef2d46249248f'
subprocess.run(['python',str(R/'tools/check_stage15_coverage.py')],check=True,cwd=R)
j=json.loads((R/'docs/檢查/階段1.5目前覆蓋與R1檢查.json').read_text());total=j['卡片數'];r1=j['R1後目前新增卡片數']
diff=subprocess.check_output(['git','-c','core.quotePath=false','diff','--name-status',base,'HEAD','--','qi-zheng-si-yu/knowledge'],cwd=R).decode().splitlines();assert len(diff)==42 and all(x.startswith('A\t')for x in diff)
rows=[]
for line in diff:
 p=R/line.split('\t',1)[1];t=p.read_text();assert t.startswith('#七政四餘\n')and all(t.count('## '+s)==1 for s in ['核心概念','使用規則','操作步驟','原文例子']);rows.append({'檔案':str(p.relative_to(R)),'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'日期':'2026-11-21','基準提交':base,'新增卡數':42,'原有卡異動':0,'刪除':0,'本批新增空殼':0,'卡片總數':total,'明細':rows};(R/'docs/檢查/綱目87至88頁本批總驗證-2026-11-21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for fn in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md']:
 p=R/fn;s=p.read_text();s=re.sub(r'(?m)^- 卡片[\d,]+張；R1生效後目前新增[\d,]+張',f'- 卡片{total:,}張；R1生效後目前新增{r1:,}張',s);s=re.sub(r'(?m)^- 全庫\d+卡；R1後目前新增\d+卡',f'- 全庫{total}卡；R1後目前新增{r1}卡',s);s=re.sub(r'(統計更新：[^\n]*共)[\d,]+張',lambda m:m[1]+f'{total:,}張',s)
 if '第87–88頁下表新增42卡'not in s:s+='\n2026-11-21更新：第87–88頁下表新增42卡；既有卡片異動0。第一個復工動作：第89頁下表。未明細字仍待核，不標整頁或階段完成。\n'
 p.write_text(s)
print(json.dumps({k:v for k,v in report.items()if k!='明細'},ensure_ascii=False))
