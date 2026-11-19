from pathlib import Path
import subprocess,json,re
R=Path('.');K=R/'qi-zheng-si-yu/knowledge'
def g(*a):return subprocess.check_output(['git','-c','core.quotepath=false',*a]).decode()
changes=g('diff','--name-status','30166409','--','qi-zheng-si-yu/knowledge').splitlines();names=[x.split('\t',1) for x in changes];names += [('A',x)for x in g('ls-files','--others','--exclude-standard','--','qi-zheng-si-yu/knowledge').splitlines()];rows=[]
for status,name in names:
 p=Path(name);s=p.read_text();rows.append({'檔案':p.name,'新增':status=='A','四欄':all('## '+x in s for x in ['核心概念','使用規則','操作步驟','原文例子']),'標籤':s.startswith('#七政四餘\n'),'出處':bool(re.search(r'《星學綱目正傳》第\d+頁',s))})
errors=[];p=Path('docs/檢查/綱目97至100續核範圍.md')
for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
 if not(p.parent/link).exists():errors.append(link)
checks={'4張均為新增':len(rows)==4 and all(x['新增']for x in rows),'四欄首行出處齊全':all(x['四欄']and x['標籤']and x['出處']for x in rows),'既有卡片改動0':not any(not x['新增']for x in rows),'全庫19760張':len(list(K.glob('*.md')))==19760,'報告失效連結0':not errors,'狀態前三段30行內':len(Path('docs/狀態.md').read_text().splitlines())<=30}
result={'日期':'2026-11-19','基準':'30166409','證據等級':'E0：卡片格式、檔案異動與連結檢查；人工字讀另見校讀紀錄','檢查':checks,'通過':all(checks.values()),'卡片':rows,'失效連結':errors};assert result['通過'],result
Path('docs/檢查/綱目97至100新增4卡驗證.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False))
