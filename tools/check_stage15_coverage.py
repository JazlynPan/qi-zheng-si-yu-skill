"""核對帳本頁碼列記與R1後新增空殼；不改卡，不判定原圖已核完。"""
from pathlib import Path
from collections import Counter
import json,re,subprocess,unicodedata
from stage2_preflight import parse, substantive
ROOT=Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True)
def spans(nums):
    runs=[]
    for n in sorted(nums):
        if runs and n==runs[-1][1]+1:runs[-1][1]=n
        else:runs.append([n,n])
    return runs
rows=[]
for line in (ROOT/'docs/來源清單.md').read_text().splitlines():
    if not line.startswith('|') or 'https://' not in line:continue
    c=line.strip('|').split('|');status=c[5];text=c[6]
    kind='完成' if re.search(r'首輪.*(?:完成|通過)',status) or '完成首輪提煉' in status else '進行中'
    limit=int(c[3]) if c[3].isdigit() else None
    covered=set()
    for a,b in re.findall(r'(\d+)\s*[–—-]\s*(\d+)',text):covered.update(range(int(a),int(b)+1))
    if c[0]=='河洛五星合參案例抄本' and '1、11敘事跳過' in text and '14正文空白' in text:covered.update([1,11,14,15])
    if c[0]=='星學綱目正傳' and '103、156空白' in text:covered.update([103,156])
    missing=set(range(1,limit+1))-covered if limit else set()
    rows.append({'書名':c[0],'正文帳本分類':kind,'PDF頁數':limit,'未明列範圍':spans(missing),'未明列頁數':len(missing),'限制':'列記覆蓋不等於圖表與疑字已核完；Word依原始段落，不計PDF頁數。'})
r1=git('log','--reverse','--format=%H','--','docs/規則補充.md').splitlines()[0]
added=[p for p in git('diff','--name-only','--diff-filter=A','-z',r1,'HEAD','--','qi-zheng-si-yu/knowledge').split('\0') if p]
empty=[]
for name in added:
    fields,sources,_=parse((ROOT/name).read_text())
    rest=''.join(substantive(v) for v in fields.values())
    for marker in ['原文以圖表呈現','原文以图表呈现','原文未提及','無','无']:rest=rest.replace(marker,'')
    rest=''.join(c for c in rest if not c.isspace() and not unicodedata.category(c).startswith('P'))
    if not rest:empty.append({'檔名':Path(name).name,'所屬書':sorted({s[0] for s in sources})})
report={'基準提交':git('rev-parse','HEAD').strip(),'R1生效提交':r1,'卡片數':len(list((ROOT/'qi-zheng-si-yu/knowledge').glob('*.md'))),'R1後目前新增卡片數':len(added),'R1後新增空殼數':len(empty),'新增空殼':empty,'來源數':len(rows),'PDF總頁數':sum(r['PDF頁數'] or 0 for r in rows),'正文帳本狀態':dict(Counter(r['正文帳本分類'] for r in rows)),'逐書列記覆蓋':rows,'階段1.5完成':False,'證據等級':'E0，腳本體檢；不代表原文語義或圖表驗收。'}
(ROOT/'docs/檢查/階段1.5目前覆蓋與R1檢查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['卡片數','R1後目前新增卡片數','R1後新增空殼數','來源數','PDF總頁數','正文帳本狀態']},ensure_ascii=False))
print(json.dumps([r for r in rows if r['未明列頁數']],ensure_ascii=False))
