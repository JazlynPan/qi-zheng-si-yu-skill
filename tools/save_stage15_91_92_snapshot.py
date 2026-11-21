"""執行：核對91–92頁批次、同步目前摘要數字；不改知識卡。"""
from pathlib import Path
import json,re,subprocess,hashlib
R=Path(__file__).resolve().parents[1];base='aeb2299d53d4e500d80484471fda545e10273a2c'
subprocess.run(['python',str(R/'tools/check_stage15_coverage.py')],check=True,cwd=R)
j=json.loads((R/'docs/檢查/階段1.5目前覆蓋與R1檢查.json').read_text());total=j['卡片數'];r1=j['R1後目前新增卡片數']
diff=subprocess.check_output(['git','-c','core.quotePath=false','diff','--name-status',base,'HEAD','--','qi-zheng-si-yu/knowledge'],cwd=R).decode().splitlines();assert len(diff)==32 and all(x.startswith('A\t')for x in diff)
rows=[]
for line in diff:
 p=R/line.split('\t',1)[1];t=p.read_text();assert t.startswith('#七政四餘\n')and all(t.count('## '+s)==1 for s in ['核心概念','使用規則','操作步驟','原文例子']);rows.append({'檔案':str(p.relative_to(R)),'SHA256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'日期':'2026-11-21','基準提交':base,'新增卡數':32,'原有卡異動':0,'刪除':0,'本批新增空殼':0,'卡片總數':total,'明細':rows};(R/'docs/檢查/綱目91至92頁本批總驗證-2026-11-21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for fn in ['docs/階段1.5目前檢查摘要.md','docs/檢查/階段1.5完成條件核對-2026-11-18.md']:
 p=R/fn;s=p.read_text();s=re.sub(r'(?m)^- 卡片[\d,]+張；R1生效後目前新增[\d,]+張',f'- 卡片{total:,}張；R1生效後目前新增{r1:,}張',s);s=re.sub(r'(?m)^- 全庫\d+卡；R1後目前新增\d+卡',f'- 全庫{total}卡；R1後目前新增{r1}卡',s);s=re.sub(r'(統計更新：[^\n]*共)[\d,]+張',lambda m:m[1]+f'{total:,}張',s)
 if '第91–92頁下表新增32卡'not in s:s+='\n2026-11-21更新：第91–92頁下表新增32卡；既有卡片異動0。第一個復工動作：第93頁下表。未明細字仍待核，不標整頁或階段完成。\n'
 p.write_text(s)
print(json.dumps({k:v for k,v in report.items()if k!='明細'},ensure_ascii=False))

from collections import Counter
source=R/'docs/檢查/階段1.5待校與待裁決分界.md'
positions=re.findall(r'^\|([^|]+?) (\d+)\|',source.read_text(),re.M)
counts=dict(Counter(x[0]for x in positions))
assert len(positions)==43
text='# 階段1.5剩餘頁數口徑（2026-11-21）\n\n第91–92頁本批已補32卡，未標整頁完成。正在接續的綱目下表補錄剩4頁：93–96頁。\n\n舊待核表共43個圖頁位置：'+str(counts)+'。這是跨書待核範圍，不是43頁全未讀。表內包含已裁決而未逐項更新的歷史描述，不能把43直接當作剩餘整頁數。\n\n階段1.5還有已讀頁的模糊字、圖表局部、使用者待裁決，以及全庫逐段驗收與結束前雲端盤點。完成93–96頁並不自動代表階段結束。未完成逐頁核銷前，不提供虛假的整階段剩餘頁數。\n\n[舊表來源](階段1.5待校與待裁決分界.md)；[最新狀態](../狀態.md)。\n'
(R/'docs/檢查/階段1.5剩餘頁數口徑-2026-11-21.md').write_text(text)
