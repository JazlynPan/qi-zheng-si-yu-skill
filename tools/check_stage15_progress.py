"""執行：階段1.5報告批次的本機連結、入口數量、卡片唯讀檢查；不判原字。"""
from pathlib import Path
from urllib.parse import unquote
from validate_suidian_entry_20261120 import anchors
import argparse,json,re,subprocess
R=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True);ap.add_argument('--expected-items',type=int,required=True);args=ap.parse_args()
 changed=subprocess.check_output(['git','diff','HEAD','--name-only','--','qi-zheng-si-yu/knowledge'],cwd=R).decode();added=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','qi-zheng-si-yu/knowledge'],cwd=R).decode();assert not changed and not added
 entry=(R/'docs/待你處理.md').read_text();groups={s.splitlines()[0]:len(re.findall(r'^- ',s,re.M))for s in re.split(r'^## ',entry,flags=re.M)[1:]};assert sum(groups.values())==args.expected_items
 errors=[];count=0;cache={}
 for p in R.rglob('*.md'):
  if '.git'in p.parts:continue
  for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>\n]+>|[^)\n]+)\)',p.read_text()):
   t=re.sub(r'\s+"[^"]*"$','',m[1].strip().strip('<>'))
   if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',t)or t.startswith('//'):continue
   count+=1;parts=t.split('#',1);q=(p.parent/unquote(parts[0])).resolve()if parts[0]else p
   if not q.exists():errors.append([str(p.relative_to(R)),t,'檔案不存在']);continue
   if len(parts)==2 and parts[1]and q.suffix=='.md':
    if q not in cache:cache[q]=anchors(q)
    if unquote(parts[1])not in cache[q]:errors.append([str(p.relative_to(R)),t,'錨點不存在'])
 report={'日期':'2026-11-20','證據等級':'E0，文件與唯讀檢查，不是原字裁決','卡片總數':len(list((R/'qi-zheng-si-yu/knowledge').glob('*.md'))),'卡片增刪異動':0,'待處理項數':sum(groups.values()),'各組數':groups,'本機連結數':count,'失效數':len(errors),'失效清單':errors,'狀態檔行數':len((R/'docs/狀態.md').read_text().splitlines())};(R/args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));assert not errors
if __name__=='__main__':main()
